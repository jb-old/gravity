//&>/dev/null;x="${0%.*}";[ ! "$x" -ot "$0" ]||(rm -f "$x";cc -o "$x" "$0")&&"$x" $*;exit
#include <stdio.h>
#include <stdint.h>

int main(int argc, char* argv) {
  if (isatty(fileno(stdout))) {
    fprintf(stderr, "Fatal error: stdout is an terminal.\n");
    return 1;
  }
  
  int64_t datum = 2;
  fwrite(&datum, sizeof(datum), 1, stdout);
}
