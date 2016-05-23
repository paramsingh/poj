import sys
import subprocess

if __name__ == "__main__":
    try:
        executable = sys.argv[1]
        input_filename = sys.argv[2]
        output_filename = sys.argv[3]
        tl = sys.argv[4]
    except IndexError:
        sys.exit(-1)

    input_file = open(input_filename, "r")
    output_file = open(output_filename, "w")
    returncode = subprocess.call(["timeout", tl, "./{}".format(executable)], stdin = input_file, stdout = output_file)
    print(returncode)
    input_file.close()
    output_file.close()
