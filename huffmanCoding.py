import heapq
import os

# Node structure for Huffman Tree
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    # Comparing nodes for priority queue (heapq)
    def __lt__(self, other):
        return self.freq < other.freq

# Build the frequency dictionary
def calculate_frequency(data):
    freq_dict = {}
    for char in data:
        if not char in freq_dict:
            freq_dict[char] = 0
        freq_dict[char] += 1
    return freq_dict

# Build the Huffman Tree
def build_huffman_tree(freq_dict):
    heap = []
    
    # Create a priority queue (min-heap)
    for char, freq in freq_dict.items():
        heapq.heappush(heap, HuffmanNode(char, freq))
    
    while len(heap) > 1:
        # Extract the two nodes with the lowest frequency
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        
        # Create a new internal node with these two nodes as children
        merged = HuffmanNode(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        
        # Add the merged node back into the heap
        heapq.heappush(heap, merged)
    
    # The last node remaining is the root of the Huffman Tree
    return heapq.heappop(heap)

# Generate Huffman Codes by traversing the tree
def generate_codes(node, current_code="", codes={}):
    if node is None:
        return
    
    if node.char is not None:
        # Leaf node
        codes[node.char] = current_code
    
    generate_codes(node.left, current_code + "0", codes)
    generate_codes(node.right, current_code + "1", codes)

# Encode the input data into its binary form
def huffman_encode(data, codes):
    encoded_data = ""
    for char in data:
        encoded_data += codes[char]
    return encoded_data

# Add padding to make the encoded data length a multiple of 8 (byte-aligned)
def pad_encoded_data(encoded_data):
    extra_padding = 8 - len(encoded_data) % 8
    for _ in range(extra_padding):
        encoded_data += "0"
    
    padded_info = "{0:08b}".format(extra_padding)
    encoded_data = padded_info + encoded_data
    return encoded_data

# Convert binary string into byte array
def get_byte_array(padded_encoded_data):
    if len(padded_encoded_data) % 8 != 0:
        raise ValueError("Encoded data is not byte aligned")
    
    b = bytearray()
    for i in range(0, len(padded_encoded_data), 8):
        byte = padded_encoded_data[i:i+8]
        b.append(int(byte, 2))
    
    return b

# Compress function
def compress_file(input_path):
    # Read the input file
    with open(input_path, 'r') as file:
        data = file.read().strip()
    
    # Step 1: Calculate frequency of each character
    freq_dict = calculate_frequency(data)
    
    # Step 2: Build the Huffman Tree
    huffman_tree = build_huffman_tree(freq_dict)
    
    # Step 3: Generate the Huffman Codes
    codes = {}
    generate_codes(huffman_tree, "", codes)
    
    # Step 4: Encode the input data using the Huffman Codes
    encoded_data = huffman_encode(data, codes)
    
    # Step 5: Pad the encoded data and convert it to a byte array
    padded_encoded_data = pad_encoded_data(encoded_data)
    byte_array = get_byte_array(padded_encoded_data)
    
    # Save the compressed data into a binary file
    output_path = input_path.split(".")[0] + "_compressed.bin"
    with open(output_path, 'wb') as output:
        output.write(bytes(byte_array))
    
    print(f"File compressed and saved to {output_path}")
    return output_path, huffman_tree

# Remove padding from the encoded data
def remove_padding(padded_encoded_data):
    padded_info = padded_encoded_data[:8]
    extra_padding = int(padded_info, 2)
    
    padded_encoded_data = padded_encoded_data[8:]  # Remove the padding info
    encoded_data = padded_encoded_data[:-1 * extra_padding]  # Remove the extra padding
    return encoded_data

# Decode the binary data using Huffman Tree
def decode_data(encoded_data, huffman_tree):
    current_node = huffman_tree
    decoded_data = ""
    
    for bit in encoded_data:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
        
        # If leaf node, append the character
        if current_node.left is None and current_node.right is None:
            decoded_data += current_node.char
            current_node = huffman_tree
    
    return decoded_data

# Decompress function
def decompress_file(compressed_file_path, huffman_tree):
    # Read the binary data from compressed file
    with open(compressed_file_path, 'rb') as file:
        bit_string = ""
        byte = file.read(1)
        while byte:
            byte = ord(byte)
            bits = bin(byte)[2:].rjust(8, '0')
            bit_string += bits
            byte = file.read(1)
    
    # Remove the padding from the bit string
    encoded_data = remove_padding(bit_string)
    
    # Decode the data using the Huffman Tree
    decompressed_data = decode_data(encoded_data, huffman_tree)
    
    # Save the decompressed data into a text file
    output_path = compressed_file_path.split("_compressed")[0] + "_decompressed.txt"
    with open(output_path, 'w') as output:
        output.write(decompressed_data)
    
    print(f"File decompressed and saved to {output_path}")
    return output_path

# Example usage
if __name__ == "__main__":
    input_file = "sample.txt"  # Change this to the path of your input file
    compressed_file, huffman_tree = compress_file(input_file)
    decompress_file(compressed_file, huffman_tree)
