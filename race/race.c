#include <stdio.h>
#include <pthread.h>
#define NUM_THREADS 2
int *number_args = 2;
int *ptr = NULL;

void *PrintHello(void *threadid) {
	int *pt = malloc(sizeof(int));
	ptr = NULL;
	sleep(10);
	ptr = pt;
        printf("Hello World! Thread ID 1 \n");
}

void *PrintHello1(void *threadid) {
        sleep(5);
	int pt = *ptr;
        printf("Hello World! Thread ID 2\n");
}
int main () {
	pthread_t threads[NUM_THREADS];
	int num = 10;
	int rc;
	int i;
	ptr = malloc(sizeof(int));
	printf("main() : creating thread, %d\n", 1);
	rc = pthread_create(&threads[0], NULL, PrintHello, (void *)0);
	printf("main() : creating thread, %d\n", 2);
	rc = pthread_create(&threads[1], NULL, PrintHello1, (void *)1);
	pthread_join(&threads[0], NULL);
	pthread_join(&threads[1], NULL);
	pthread_exit(NULL);
}
