#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
  srand(time(0));
  for (int i = 0; i < 5; i++) {
    printf("%i\n", rand() % 3);
  }
  return 0;
}
