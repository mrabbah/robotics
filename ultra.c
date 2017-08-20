#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <pthread.h>
#include <wiringPi.h>


int main ()
{
	if (wiringPiSetup () == -1)
	{
	fprintf (stdout, "oops: %s\n", strerror (errno)) ;
	return 1 ;
	}

	pinMode (0, OUTPUT) ;

	
}
