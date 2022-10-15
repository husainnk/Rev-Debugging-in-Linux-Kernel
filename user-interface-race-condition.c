
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>


#define NUM_THREADS 2

static int *number_args;

void *PrintHello(void *threadid) {
        long tid;
        tid = (long)threadid;
        if(tid == 0 )
                {       int *temp = number_args;
                        *number_args = NULL;
                        sleep(10);
                        number_args = temp;
                }
        else
                {*number_args = 1;}
        printf("Hello World! Thread ID, %ld\n", tid);
        pthread_exit(NULL);
}

int main () {
   pthread_t threads[NUM_THREADS];
   int num = 10;
   int rc;
   int i;
   number_args = &num;
   for( i = 0; i < NUM_THREADS; i++ ) {
      printf("main() : creating thread, %d\n", i);
      rc = pthread_create(&threads[i], NULL, PrintHello, (void *)i);
      if (rc) {
         printf("Error:unable to create thread, %d\n", rc);

      }
   }
}

