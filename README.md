# discourse_unsubscriber: Unsubscribe from Discourse threads easily

Unsubscribe from Discourse threads from your mutt

10r/min seems to be the limit. Investigate further.

# --client
* [X] Submit job to the submit queue
* [X] Fork off
* [X] Listen on the status queue and print status
# --server
* [X] Listen on the submit queue
* [X] Send to discourse
  * [ ] Follow the limits
  * [ ] Retry with https://github.com/jd/tenacity
* [X] Send to status queue
