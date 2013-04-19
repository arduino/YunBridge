/*
  Copyright (c) 2013 Arduino LLC. All right reserved.

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
*/

#include <FileIO.h>

File::File() : mode(255), filename(NULL) {
  // Empty
}

File::File(const char *_filename, uint8_t _mode) : mode(_mode) {
  filename = new char[strlen(_filename)+1];
  strcpy(filename, _filename);
}

File::operator bool() {
  return (mode != 255);
}

File::~File() {
  if (filename)
    delete[] filename;
}

char toHex(uint8_t c) {
  if (c<10)
    return '0' + c;
  else
    return 'A' + c - 10;
}

size_t File::write(uint8_t c) {
  Process echo;
  echo.begin("arduino-append");
  echo.addParameter(filename);
  char chars[] = { '\\', 'x', toHex(c >> 4), toHex(c & 0x0F), '\0' };
  echo.addParameter(chars);
  echo.run();
  return 1;
}

size_t File::write(const uint8_t *buf, size_t size) {
  Process echo;
  echo.begin("arduino-append");
  echo.addParameter(filename);
  echo.addParameter(" \"", true);
  for (unsigned int i=0; i<size; i++) {
    // slow but requires less memory
    char c = buf[i];
    char chars[] = { '\\', 'x', toHex(c >> 4), toHex(c & 0x0F), '\0' };
    echo.addParameter(chars, true);
  }
  echo.addParameter("\"", true);
  echo.run();
  return size;
}

int File::read() {
  return 1;
}

int File::peek() {
  return 1;
}

int File::available() {
  return 1;
}

void File::flush() {
}

//int read(void *buf, uint16_t nbyte)
//boolean seek(uint32_t pos)
//uint32_t position()
//uint32_t size()

void File::close() {
  mode = 255;
}

char *name() {
  return filename;
}

//boolean isDirectory(void)
//File openNextFile(uint8_t mode = O_RDONLY);
//void rewindDirectory(void)






boolean SDClass::begin() {
  return true;
}

File SDClass::open(const char *filename, uint8_t mode) {
  if (mode == FILE_READ) {
    if (exists(filename))
      return File(filename, mode);
  }
  if (mode == FILE_WRITE) {
    Process touch;
    touch.begin(">");
    touch.addParameter(filename);
    int res = touch.run();
    if (res == 0)
      return File(filename, mode);
  }
  return File();
}

boolean SDClass::exists(const char *filepath) {
  Process ls;
  ls.begin("ls");
  ls.addParameter(filepath);
  int res = ls.run();
  return (res == 0);
}

boolean SDClass::mkdir(const char *filepath) {
  Process mk;
  mk.begin("mkdir");
  mk.addParameter("-p");
  mk.addParameter(filepath);
  int res = mk.run();
  return (res == 0);
}

boolean SDClass::remove(const char *filepath) {
  Process rm;
  rm.begin("rm");
  rm.addParameter(filepath);
  int res = rm.run();
  return (res == 0);
}

boolean SDClass::rmdir(const char *filepath) {
  Process rm;
  rm.begin("rmdir");
  rm.addParameter(filepath);
  int res = rm.run();
  return (res == 0);
}

SDClass SD;