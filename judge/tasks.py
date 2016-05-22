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
    input_filename = tc.input_file.name.split("/")[1]
    output_filename = tc.output_file.name.split("/")[1]
    print("input = {}, output = {}".format(input_filename, output_filename))
    # first create a new docker container of the image poj
    container_id = subprocess.check_output(["docker", "run", "-it", "-m","256M","-d", "poj"])
    # decode bytestring to utf-8 and remove the last newline from docker output
    container_id = container_id.decode('utf-8')
    print(container_id)
    container_id = container_id[:len(container_id)-1]
    docker_lst  = ["docker", "exec", container_id]
    # copy input and output files to docker container
    subprocess.call(["docker", "exec", container_id, "mkdir", "testcases"])
    subprocess.call(["docker", "cp", tc.input_file.name, "{}:/{}".format(container_id, input_filename)])
    subprocess.call(["docker", "cp", tc.output_file.name, "{}:/{}".format(container_id, output_filename)])
    tl = cur_problem.time_limit
    timeout_lst = ["timeout", str(tl)]
    user_output = "{}.{}.output".format(username, sub_id)
    filename = ''
    compiler = ''
    if submission.lang == "C":
        filename = "{}.{}.c".format(username, sub_id)
        compiler = 'gcc'
    elif submission.lang == "CPP":
        filename = "{}.{}.cpp".format(username, sub_id)
        compiler = 'g++'

    executable = "{}.{}.out".format(username, sub_id)
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
        inputfile = open(tc.input_file.name, "r")
        user_output_file_name = "{}.{}.output".format(username, sub_id)
        user_output_file = open(user_output_file_name, "w")
        options_lst = ["./{}".format(executable)] 
        run_code = subprocess.call(timeout_lst + docker_lst + options_lst, stdin = inputfile, stdout = user_output_file)
        user_output_file.close()
        inputfile.close()
        subprocess.call(["docker", "cp", user_output_file_name, "{}:/{}".format(container_id, user_output_file_name)])
        subprocess.call(["docker", "exec", container_id, "ls"])
        if run_code == 124:
            # time limit exceeded
            print("time limit exceeded")
            submission.status = "TL"
            submission.save()
            cur_problem.num_tle += 1
            cur_problem.save()
            print('HI')
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
            differences = subprocess.call(docker_lst + ["diff", user_output, output_filename])
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
        os.remove(user_output_file_name)
    os.remove("submissions/{}".format(filename))

    subprocess.call(["docker", "stop", container_id])