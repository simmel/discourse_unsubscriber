# discourse_unsubscriber: Unsubscribe from Discourse threads easily

Unsubscribe from Discourse threads from your mutt

10r/min seems to be the limit. Investigate further.

* [X] Make loglevel WARNING or ERROR default
* [X] Add verbose flag which uses INFO logging and log every URL we visit
# --client
* [X] Submit job to the submit queue
* [X] Fork off
* [X] Listen on the status queue and print status
# --server
* [X] Listen on the submit queue
* [X] Send to discourse
  * [X] Follow the limits
  * [X] Retry with https://github.com/jd/tenacity
  * [ ] Find a better way to make sure it's only 10r/min.
  * [ ] Get better logging of retry. Reimplement after_log
* [X] Send to status queue
