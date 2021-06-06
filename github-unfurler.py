import os
import consts
import github

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
github_client = github.Github()


repos = dict()
for repo in consts.REPOS:
    repos[repo] = github_client.get_repo(repo)


# Check liveness
@app.event("app_mention")
def event_test(say):
    say("Yes?")


@app.event("link_shared")
def got_link(client, payload):
    for link in payload["links"]:
        pr_id, repo_str = get_repo_str(link)

        import ipdb
        ipdb.set_trace()

        pull = repos[repo_str].get_pull(int(pr_id))

        _payload = get_payload(link["url"]  , pull)
        channel_id = payload["channel"]
        client.chat_unfurl(
            channel=channel_id,
            ts=payload["message_ts"],
            unfurls=_payload,
        )


def get_repo_str(link):
    url = link["url"]
    url, pr_id = url.rsplit("/", 1)
    url, _ = url.rsplit("/", 1)
    repo_str = url.replace("https://github.com/", "")
    return pr_id, repo_str


def get_payload(url, pull):
    status = pull.state
    title = pull.title
    unfurl_text = f":github: [*{status}*] : {title}"

    payload = {
        url: {
            "color": "#025BA6",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": unfurl_text,
                    }
                },
            ]
        }
    }
    return payload

if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()