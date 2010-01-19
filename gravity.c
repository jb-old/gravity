/*
 * input is textual, output is binary
 *
 * input consists of a whitespace-seperated list of argumented
 * commands, all of the option commands (all but OBJECT) override any
 * previous instance of the same command, and each occurence of OBJECT
 * specifies the state of a new object at T=0 in the system. the
 * available commands and their arguments are as follows:
 * - DIMENSIONS $width=768 $height=512
 * - CENTRE $x_offset=0 $y_offset=0
 * - FRAMES $frames=1001
 * - ZOOM $magnification=1
 * - DT $elapsed_time=60*60*24*365.2425
 * - TI $initial_time=0
 * - G $gravitational_constant=6.67428e-11
 * - MERGING $merge_colliding_objects=1
 * - OBJECT $mass $radius
 *          $x_displacement $y_displacement
 *          $x_velocity $y_velocity
 */

#include <stdio.h>
#include <stdint.h>

int gravity_main(FILE* input, FILE* output) {
  fprintf(stderr, "Fatal error: I haven't coded anything yet!\n");
  
  return 1;
}
