# Frequently Asked Questions

 1. [An error occurred while accessing Grafana](#an-error-occurred-while-accessing-grafana)
 2. ["xx" is an invalid ISO8601 timespan duration.](#xx-is-an-invalid-iso8601-timespan-duration)

## "An error occurred while accessing Grafana"
This error indicates an issue with communication or authentication to Grafana. There are a couple of things you can check

 1. Check that the Grafana API key is correct.
    * You may seem someing in the Nautobot worker logs that indicate an authentication failure. 
    `Request returned 401 for https://<grafana_url>/render/d-solo/<dashboard_id>/<dashboard_name>` would indicate that
    the API key is incorrect.
    
 2. Check that the Grafana base URL is correct.
    * If you receive a similar error, but the Nautobot worker logs state `An error occurred while accessing the url`, you
    will need to ensure that the base url for Grafana is set correctly.
    
 3. Check that the Nautobot server is able to access the Grafana application over the service port, usually https (443).
    * If the error specified takes longer than expected to return, it could be that the ChatOps service is waiting for a
    response from the Grafana application, but the port is not opened. 
    * An indication of this in the Nautobot worker logs would be a `An error occurred while accessing the url` error message
    along with a `'Connection to <grafana_host> timed out. (connect timeout=60)')` message.
    
##  "xx" is an invalid ISO8601 timespan duration.
This error is an indication that the timespan option was passed in the chat command, however, the timespan value
that was passed in is unable to be decoded by the plugin. See the [ISO_8601 Durations](https://en.wikipedia.org/wiki/ISO_8601#Durations)
for full documentation, but a snippet is provided below for common uses.

  * `P` is the duration designator (for period) placed at the start of the duration representation.
    * `Y` is the year designator that follows the value for the number of years.
    * `M` is the month designator that follows the value for the number of months.
    * `W` is the week designator that follows the value for the number of weeks.
    * `D` is the day designator that follows the value for the number of days.
    
  * `T` is the time designator that precedes the time components of the representation.
    * `H` is the hour designator that follows the value for the number of hours.
    * `M` is the minute designator that follows the value for the number of minutes.
    * `S` is the second designator that follows the value for the number of seconds.

For example, if we wanted to see a graph containing data for the last 12 months, we would define a `timespan=P12M`.