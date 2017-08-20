#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <pthread.h>
#include <wiringPi.h>
#include <softServo.h>

#define	MAX_SERVOS	8

static int pinMap     [MAX_SERVOS] ;	// Keep track of our pins
static int pulseWidth [MAX_SERVOS] ;	// microseconds


/*
 * softServoThread:
 *	Thread to do the actual Servo PWM output
 *********************************************************************************
 */

static PI_THREAD (softServoThread)
{
  register int i, j, k, m, tmp ;
  int lastDelay, pin, servo ;

  int myDelays [MAX_SERVOS] ;
  int myPins   [MAX_SERVOS] ;

  struct timeval  tNow, tStart, tPeriod, tGap, tTotal ;
  struct timespec tNs ;

  tTotal.tv_sec  =    0 ;
  tTotal.tv_usec = 8000 ;

  piHiPri (50) ;

  for (;;)
  {
    gettimeofday (&tStart, NULL) ;

    memcpy (myDelays, pulseWidth, sizeof (myDelays)) ;
    memcpy (myPins,   pinMap,     sizeof (myPins)) ;

// Sort the delays (& pins), shortest first

    for (m = MAX_SERVOS / 2 ; m > 0 ; m /= 2 )
      for (j = m ; j < MAX_SERVOS ; ++j)
	for (i = j - m ; i >= 0 ; i -= m)
	{
	  k = i + m ;
	  if (myDelays [k] >= myDelays [i])
	    break ;
	  else // Swap
	  {
	    tmp = myDelays [i] ; myDelays [i] = myDelays [k] ; myDelays [k] = tmp ;
	    tmp = myPins   [i] ; myPins   [i] = myPins   [k] ; myPins   [k] = tmp ;
	  }
	}

// All on

    lastDelay = 0 ;
    for (servo = 0 ; servo < MAX_SERVOS ; ++servo)
    {
      if ((pin = myPins [servo]) == -1)
	continue ;

      digitalWrite (pin, HIGH) ;
      myDelays [servo] = myDelays [servo] - lastDelay ;
      lastDelay += myDelays [servo] ;
    }

// Now loop, turning them all off as required

    for (servo = 0 ; servo < MAX_SERVOS ; ++servo)
    {
      if ((pin = myPins [servo]) == -1)
	continue ;

      delayMicroseconds (myDelays [servo]) ;
      digitalWrite (pin, LOW) ;
    }

// Wait until the end of an 8mS time-slot

    gettimeofday (&tNow, NULL) ;
    timersub (&tNow, &tStart, &tPeriod) ;
    timersub (&tTotal, &tPeriod, &tGap) ;
    tNs.tv_sec  = tGap.tv_sec ;
    tNs.tv_nsec = tGap.tv_usec * 1000 ;
    nanosleep (&tNs, NULL) ;
  }

  return NULL ;
}


/*
 * softServoWrite:
 *	Write a Servo value to the given pin
 *********************************************************************************
 */

void softServoWrite (int servoPin, int value)
{
  int servo ;

  servoPin &= 63 ;

  /**/ if (value < -250)
    value = -250 ;
  else if (value > 1250)
    value = 1250 ;

  for (servo = 0 ; servo < MAX_SERVOS ; ++servo)
    if (pinMap [servo] == servoPin)
      pulseWidth [servo] = value + 1000 ; // uS
}


/*
 * softServoSetup:
 *	Setup the software servo system
 *********************************************************************************
 */

int softServoSetup (int p0, int p1, int p2, int p3, int p4, int p5, int p6, int p7)
{
  int servo ;

  if (p0 != -1) { pinMode (p0, OUTPUT) ; digitalWrite (p0, LOW) ; }
  if (p1 != -1) { pinMode (p1, OUTPUT) ; digitalWrite (p1, LOW) ; }
  if (p2 != -1) { pinMode (p2, OUTPUT) ; digitalWrite (p2, LOW) ; }
  if (p3 != -1) { pinMode (p3, OUTPUT) ; digitalWrite (p3, LOW) ; }
  if (p4 != -1) { pinMode (p4, OUTPUT) ; digitalWrite (p4, LOW) ; }
  if (p5 != -1) { pinMode (p5, OUTPUT) ; digitalWrite (p5, LOW) ; }
  if (p6 != -1) { pinMode (p6, OUTPUT) ; digitalWrite (p6, LOW) ; }
  if (p7 != -1) { pinMode (p7, OUTPUT) ; digitalWrite (p7, LOW) ; }

  pinMap [0] = p0 ;
  pinMap [1] = p1 ;
  pinMap [2] = p2 ;
  pinMap [3] = p3 ;
  pinMap [4] = p4 ;
  pinMap [5] = p5 ;
  pinMap [6] = p6 ;
  pinMap [7] = p7 ;

  for (servo = 0 ; servo < MAX_SERVOS ; ++servo)
    pulseWidth [servo] = 1500 ;		// Mid point
  
  return piThreadCreate (softServoThread) ;
}

int main ()
{
	if (wiringPiSetup () == -1)
	{
	fprintf (stdout, "oops: %s\n", strerror (errno)) ;
	return 1 ;
	}

	//softServoSetup (3, 6, -1, -1, -1, -1, -1, -1) ;

	//softServoWrite (3,  500) ;
	//softServoWrite (6, 1000) ;
	pinMode (3, OUTPUT) ;
        pinMode (6, OUTPUT) ;
        pinMode (4, OUTPUT) ;
        pinMode (5, OUTPUT) ;
        pinMode (0, OUTPUT) ;
        pinMode (2, OUTPUT) ;
	
	//ARMING MOTORS
        digitalWrite (3, HIGH) ;
        digitalWrite (6, HIGH) ;  
		
	//GO FORWARD
        digitalWrite (4, LOW) ; 		
	digitalWrite (5, HIGH) ; 
        digitalWrite (0, HIGH) ; 
        digitalWrite (2, LOW) ; 
	delay (4000) ;	
	//GO BACKWARD
        digitalWrite (4, HIGH) ; 
        digitalWrite (5, HIGH) ; 
        digitalWrite (0, HIGH) ; 
        digitalWrite (2, HIGH) ; 
	delay(2000);
	return 0;
}
