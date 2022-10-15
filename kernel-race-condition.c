#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kthread.h>  // for threads
#include <linux/sched.h>  // for task_struct
#include <linux/time.h>   // for using jiffies 
#include <linux/timer.h>
#include <linux/slab.h>
#include <linux/delay.h>

#define NUM_THREADS 2

static int *race_pointer;
static int index;
static struct task_struct *threads[NUM_THREADS];

int PrintHello(void *threadid) {
        int tid;
        int delay = 10;

        tid = *(int *)threadid;
        printk(KERN_INFO "PrintHello: Thread ID %d", tid);

        if(tid == 0 ) {
            int *temp = race_pointer;
            race_pointer = NULL;
            printk(KERN_INFO "Race Pointer is NULL now");

            msleep(delay*1000);
            
            race_pointer = temp;
            printk(KERN_INFO "Race Pointer is RESET now");
        }
        else {
            *race_pointer = 1;
        }
        printk(KERN_INFO "Hello World! Thread ID %d", tid);
        return 0;
}

int threads_init (void) {
   char thread_names[NUM_THREADS][10] = {"thread1", "thread2"};

   race_pointer = kmalloc(sizeof(int), GFP_KERNEL);
   if(!race_pointer) {
        printk(KERN_ERR "Unable to create memory for race_pointer");
        return 0;
   }
   
   *race_pointer = 2;

   for( index = 0; index < NUM_THREADS; index++ ) {
      printk(KERN_INFO "INIT : creating thread %d", index);

      threads[index] = kthread_create(PrintHello, &index, thread_names[index]);
      if (!threads[index]) {
        printk(KERN_ERR "Error:unable to create thread %d", index);
      }
      else {
        printk(KERN_INFO "Wake Up Thread %d", index);
        wake_up_process(threads[index]);
        msleep(1);
      }
   }
   return 0;
}

void threads_cleanup(void) {
    int ret;
    int i;

    for (i = 0; i < NUM_THREADS; i++)
    {
        ret = kthread_stop(threads[i]);
        if(!ret)
            printk(KERN_INFO "Thread %d stopped", i);   
    }
    kfree(race_pointer);
}

MODULE_LICENSE("GPL");   
module_init(threads_init);
module_exit(threads_cleanup);