def remove_region_from_file(input_filename, output_filename):
    with open(input_filename, 'r') as infile:
        data = infile.read()
        
    result = set()  # Using a set to store unique lines
    for line in data.split('\n'):
        parts = line.split('|')
        if len(parts) == 3:
            result.add(f"{parts[0]}|{parts[1]}")  # Add to set for uniqueness
    
    with open(output_filename, 'w') as outfile:
        outfile.write('\n'.join(result))

input_filename = 'result.txt'  # Ganti dengan nama file input yang sesuai
output_filename = 'aws_key.txt'
remove_region_from_file(input_filename, output_filename)

print(f"Output disimpan di {output_filename}")