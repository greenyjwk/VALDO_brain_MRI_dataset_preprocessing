from registration import registration_runner
from skull_stripped import skull_stripped_runner
from bias_field_correction import bias_field_correction_runner

def main():
    file_path_analysis()
    registration_runner()
    skull_stripped_runner()
    bias_field_correction_runner()

if __name__ == "__main__":
    main()