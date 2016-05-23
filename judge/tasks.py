from celery.decorators import task
from judge.models import Coder, Submission, Problem, TestCase
import subprocess
import os

@task(name="evaluate_submission")
def evaluate_submission(sub_id):
    try:
        submission = Submission.objects.get(pk = sub_id)
    except:
        print("Submission with id = {} not found".format(sub_id))
        return
    username = submission.submitter.user.username
    cur_problem = submission.problem
    cur_problem.num_submissions += 1
    tc = TestCase.objects.get(problem = cur_problem)
    ## this is real spaghetti code written in 2 hours
    # input_filename and output_filename only contain the file names such as 1.in, 2.out etc
    # tc.input_file.name on the other hand contains testcases/ (example: testcases/1.in)
    input_filename = tc.input_file.name.split("/")[1]
    output_filename = tc.output_file.name.split("/")[1]
    print("input = {}, output = {}".format(input_filename, output_filename))


    # first create a new docker container of the image poj with memory limit 256M so
    # user code does not kill the server
    container_id = subprocess.check_output(["docker", "run", "-it", "-m","256M","-d", "poj"])
    # decode bytestring to utf-8 and remove the last newline from docker output
    container_id = container_id.decode('utf-8')
    print(container_id)
    container_id = container_id[:len(container_id)-1]

    # this list can be appended to any command to make it run in container_id
    docker_lst  = ["docker", "exec", container_id]
    # first we'll copy our test case input and output files to the docker container
    # for this first we create a folder called testcases in the container
    # then move on to two docker cp commands
    subprocess.call(["docker", "exec", container_id, "mkdir", "testcases"])
    subprocess.call(["docker", "cp", tc.input_file.name, "{}:/{}".format(container_id, input_filename)])
    subprocess.call(["docker", "cp", tc.output_file.name, "{}:/{}".format(container_id, output_filename)])

    # the timeout_lst list makes sure that the user code does not run over the time limit
    # it makes use of the standard unix timeout command
    tl = cur_problem.time_limit
    timeout_lst = ["timeout", str(tl)]

    filename = '' # filename contains the name of the file which will contain the user's source code
    compiler = ''
    if submission.lang == "C":
        filename = "{}.{}.c".format(username, sub_id)
        compiler = 'gcc'
    elif submission.lang == "CPP":
        filename = "{}.{}.cpp".format(username, sub_id)
        compiler = 'g++'

    executable = "{}.{}.out".format(username, sub_id)

    # converting the user's submitted code into a file that can be compiled here
    # file will be stored in submissions/
    print("creating a file for the submitted source code")
    user_code = open("submissions/{}".format(filename), "w+")
    print(submission.code, file = user_code)
    user_code.close()
    print("file creation completed")
    print("copying file to docker container")
    subprocess.call(["docker", "cp", "submissions/{}".format(filename), "{}:/{}".format(container_id, filename)])
    print("trying to compile submission")
    compiled = subprocess.call(docker_lst + [compiler, filename, "-lm", "-o", executable])
    if compiled != 0:
        print("submission didn't compile")
        submission.status = "CE"
        cur_problem.num_ce += 1
        cur_problem.save()
        submission.save()
    else:
        print("submission compiled successfully")
        print("running the submission")
        user_output_filename = "{}.{}.output".format(username, sub_id)
        # okay this is what we do while judging
        # first we have a script call run.py which calls the compiled executable with appropriate input
        # we run this script inside our docker container
        # the script prints the output of the timeout command that it runs
        # timeout returns 124 if the program has timed out
        # we read this input and then make judgement accordingly
        options_lst = ["python3", "run.py", executable, input_filename, user_output_filename, str(tl)]
        print(docker_lst + options_lst)
        subprocess.call(["docker", "cp", "run.py", "{}:/run.py".format(container_id)])
        run_code = subprocess.check_output(docker_lst + options_lst)
        print(run_code)
        run_code = int(run_code.decode("utf-8"))
        if run_code == 124:
            # time limit exceeded
            print("time limit exceeded")
            submission.status = "TL"
            submission.save()
            cur_problem.num_tle += 1
            cur_problem.save()
        elif run_code != 0:
            # run time error
            print("run time error")
            submission.status = "RE"
            submission.save()
            cur_problem.num_re += 1
            cur_problem.save()
        else:
            print("code ran in time, now have to check with output")
            # will use diff for that, diff returns 0 if no differences, non zero if there are
            # differences or if something bad happens
            subprocess.call(["docker", "cp", "{}:/{}".format(container_id, user_output_filename), "outputs/{}".format(user_output_filename)])
            differences = subprocess.call(["diff", "outputs/{}".format(user_output_filename), tc.output_file.name])
            if not differences:
                # output is correct, done
                submission.status = "AC"
                submission.save()
                cur_problem.num_ac += 1
                cur_problem.save()
            else:
                submission.status = "WA"
                submission.save()
                cur_problem.num_wa += 1
                cur_problem.save()
    os.remove("submissions/{}".format(filename))

    subprocess.call(["docker", "stop", container_id])
