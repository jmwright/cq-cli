import os, tempfile
import tests.test_helpers as helpers

def test_semb_codec():
    """
    Basic test of the semb codec plugin.
    """
    test_file = helpers.get_test_file_location("cube.py")

    # Create a temporary file to put the semb JSON output into
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, "temp_semb.json")
    temp_error_file = os.path.join(temp_dir, "temp_semb_error.txt")

    command = ["./cq-cli.py", "--codec", "semb", "--infile", test_file, "--outfile", temp_file, "--errfile", temp_error_file]
    out, err, exitcode = helpers.cli_call(command)

    # Read the temporary JSON file back in
    with open(temp_file, 'r') as file:
        semb_str = file.read()

    assert semb_str.split('\n')[-1] == "semb_process_finished"