def calculate_latency(file_path="text/latency_record.txt"):
    # Initialize variables for sum and count
    total_sum = 0
    line_count = 0

    # Open the file in read mode
    with open(file_path, "r") as file:
        # Iterate through each line in the file
        for line in file:
            # Convert each line to an float (assuming the file contains numeric values)
            try:
                num = float(line.strip())
                total_sum += num
                line_count += 1
            except ValueError:
                continue
                print(number and case)
                # print(f"Ignoring non-numeric line: {line.strip()}")

    # Calculate the average
    if line_count > 0:
        average = total_sum / line_count
        print("Latency report")
        print(f"\tSum: {total_sum} seconds")
        print(f"\tLine Count: {line_count}")
        print(f"\tAverage: {average:.2f} seconds for each transcription")
    else:
        print("No numeric values found in the file.")

calculate_latency()