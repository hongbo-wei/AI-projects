# write a program to find the length of transcription from the file test_transcription.txt
def total_length(filename):
    total = 0
    with open(filename, 'r') as file:
        for line in file:
            total += len(line.split())  # Remove leading and trailing whitespace characters
    return total

file = 'text/test_transcription.txt'
total_length = total_length(file)
print(total_length)