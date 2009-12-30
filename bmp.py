#!/usr/bin/env python3.1
"""
                           
 i          (jeremy banks) 
 get annoyed at the format 
 BMP and finally made this 
                           
 here you go, mit licensed 
                           
i often find myself wanting to output image files and wanting to avoid
much in the way of dependencies. the easiest solution that's
widely-supported (and consequently easy to convert to other formats)
is the 24-bit windows bitmap image.

here's what the header looks like. i've included "default" values,
which are what you'll probably be using. all values are little-edian
and unsigned unless otherwise indicated.

  size default description
  ---- ------- -----------
   2 B  'BM'   "magic number" file type identifier
   4 B         file size (bytes)
   4 B    0    reserved/unused
   4 B   54    offset of bitmap data
   4 B   40    size (bytes) of second part of header
   4 B         (signed) width of image
   4 B         (signed) negative height of image
   2 B    1    "color planes" used
   2 B   24    bits per pixel, 32 adds alpha
   4 B    0    compression type used
   4 B         bitmap data size (bytes)
   4 B    0    (signed) horizontal resolution (pixel per metre)
   4 B    0    (signed) vertical resolution (pixel per metre)
   4 B    0    number of colors in color palette
   4 B    0    number of "important" colors in color palette
 (54 B total)

things to keep in mind about the data itself:
 - the number of bytes in each each row of the image must be padded to
   a multiple of four
 - the rows are stored "upside-down" by default, but we don't do this
   because we store the height of the image negative instead
 - for 24-bit images, the byte order is blue-green-red, i think alpha
   is on the end for 32-bit.

here follows a simple python script 3 that outputs a bitmap image file.

"""

import sys
import struct

HEADER_FORMAT = ( "2s" # magic number
                  "I"  # file size
                  "4x" # (reserved/unused)
                  "II" # 54, 40
                  "ii" # width, -height
                  "HHI" # 1, 24, 0
                  "I"  # bitmap data size (bytes)
                  "iiII") # 0, 0, 0, 0

def write_24bbmp(stream, dimensions, data):
    """dimensions should be (width, height)
       data should be r, g, b = data[y][x]"""
    
    width, height = dimensions
    row_bytes = width * 3
    
    if row_bytes % 4 == 0:
        row_padding = 0
    else:
        row_padding = 4 - (row_bytes % 4)
    
    data_size = 3 * height * (width + row_padding)
    file_size = data_size + 54
    
    stream.write(struct.pack(HEADER_FORMAT,
                             "BM", file_size, 54,
                             50, width, -height, 1,
                             24, 0, data_size, 0,
                             0, 0, 0))
    
    for y in range(height):
        for x in range(width):
            BGR = reversed(data[y][x])
            stream.write(bytes(BGR))
        for i in range(row_padding):
            stream.write(b"-")

def main():
    WHITE = (255, 255, 255)
    BLACK = (  0,   0,   0)
    
    with open("out.bmp", "wb") as f:
        write_24bbmp(f, (3, 2), [ [ BLACK, BLACK, BLACK ],
                                  [ WHITE, BLACK, WHITE ] ])

if __name__ == "__main__":
    main()

