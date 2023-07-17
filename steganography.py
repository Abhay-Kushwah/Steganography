#Data Shielding using Steganography

#Open terminal
#pip install opencv-python
import cv2
import os

def split(codepoint):
    red = codepoint & 3 # 00000011
    green = (codepoint & 28) >> 2 # 00011100
    blue = (codepoint & 224) >> 5 # 11100000
    return (blue, green, red)

def merge_bits(bits):
    return (((bits[0]<<3) | bits[1])<<2)|bits[2]

def make_header(file_to_embed):
    if os.path.exists(file_to_embed):
        name = os.path.basename(file_to_embed)
        size = os.path.getsize(file_to_embed)
        header = name + "," + str(size)
        if len(header) < 30:
            header = header.rjust(30, "#")
        elif len(header) > 30:
            header = header[len(header)- 30:]
        return header
    else:
        return None


def embed(source_image, file_to_embed, target_image):
    #Load the source_image in memory
    memory_image = cv2.imread(source_image)

    #Compose the header
    header = make_header(file_to_embed)

    if header is None:
        print(f"{file_to_embed} doesnt exists")
        return False

    #Load the file to embed in memory
    file_handle = open(file_to_embed, "rb")
    buffer = file_handle.read()
    file_handle.close()

    #Embedding Capacity check
    # print(memory_image.shape) # (height, width, depth)
    height = memory_image.shape[0]
    width = memory_image.shape[1]
    file_size = len(buffer)
    header_size = len(header)

    if file_size + header_size > height *width:
        print(f"{file_to_embed} too big, to embed in to {source_image}")
        return False

    #Embed Header
    for i in range(header_size):
        # pixel to embed into
        row = i // width
        col = i % width
        pixel = memory_image[row][col]
        # data to embed
        data = ord(header[i])
        bgr = split(data)
        # embedding
        pixel[0] = (pixel[0] & 248) | bgr[0]
        pixel[1] = (pixel[1] & 248) | bgr[1]
        pixel[2] = (pixel[2] & 252) | bgr[2]

    #Embed File
    for i in range(file_size):
        #pixel to embed into
        row = (i + header_size) // width
        col = (i + header_size) % width
        pixel = memory_image[row][col]
        #data to embed
        data = buffer[i]
        bgr = split(data)
        #embedding
        pixel[0] = (pixel[0] & 248) | bgr[0]
        pixel[1] = (pixel[1] & 248) | bgr[1]
        pixel[2] = (pixel[2] & 252) | bgr[2]

    #save back
    cv2.imwrite(target_image, memory_image)

    #return status
    return True

def extract(image_having_embedding):
    # Load the image in memory
    memory_image = cv2.imread(image_having_embedding)
    if memory_image is None:
        return f"{image_having_embedding} NOT READABLE!!!"

    #Know the size of the image matrix
    height = memory_image.shape[0]
    width = memory_image.shape[1]

    #Read its header_size bytes to know what is embedded inside
    header_size = 30
    header = ''
    for i in range(header_size):
        # pixel to extract from
        row = i // width
        col = i % width
        pixel = memory_image[row][col]

        #read the 3-3-2 bits from the pixel
        b = pixel[0] & 7 #00000111
        g = pixel[1] & 7 #00000111
        r = pixel[2] & 3 #00000011

        data = merge_bits((b,g,r))
        header= header + chr(data)

    try:
        #print(header + " is extracted :)")
        #Extracting the file name and file size from the header
        header = header.lstrip("#")
        file_name, file_size = header.split(",")
        file_name = "d:/temp/" + file_name
        file_size = int(file_size) #Assumed file_size : 114400
    except:
        #if error occured
        return "No Embedding Found!!!"

    #Extract the file content and start storing (writing) it.
    file_handle = open(file_name, "wb")

    for i in range(header_size, file_size+ header_size):#30 to 114400 + 30
        # pixel to extract from
        row = i // width
        col = i % width
        pixel = memory_image[row][col]

        #read the 3-3-2 bits from the pixel
        b = pixel[0] & 7 #00000111
        g = pixel[1] & 7 #00000111
        r = pixel[2] & 3 #00000011

        data = merge_bits((b,g,r))
        #data is of type : numpy int
        #it needs to be converted into byte before writing into the file
        data = int.to_bytes(int(data),1,"big") #int(data), size 1 byte, MSB is at left and lsb is at right
        file_handle.write(data)

    file_handle.close()
    return file_name


def main():
    while True:
        print("Welcome to Steganography System")
        print("1. Embed")
        print("2. Extract")
        print("3. Exit")
        print("Enter Choice")
        ch = int(input())

        if ch == 1:
            print("Enter the vessel image name")
            source_image = input() #"d:/images/jungle.png"
            print("Enter the name of file to embed ")
            file_to_embed = input() #"d:/algorithm.pdf"
            print("Enter the name of target image file") #be sure that it is a .png
            target_image = input() #"d:/temp/jungle.png"
            if embed(source_image, file_to_embed, target_image):
                print("Embedding Successful!!!")
            else:
                print("Embedding Failed!!!")

        elif ch == 2:
            print("Enter the name of image file having embedding")
            file_having_embedding = input()  # "d:/temp/jungle.png"
            temp = extract(file_having_embedding)
            print("Result: "+ temp)

        elif ch == 3:
            break

        else:
            print("Wrong Choice")

main()
