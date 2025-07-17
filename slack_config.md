## App Credentials

These credentials allow your app to access the Slack API. They are secret. Please don't share your app credentials with anyone, include them in public code repositories, or store them in insecure ways.

App ID[ ]

```
A09654D38VC
```

Date of App Creation[ ]

```
July 17, 2025
```


Client ID[ ] Client Secret[ ]

```
7050771689042.9209149110998
```

Client Secret[ ]

```
144b060b6eb3416c9fcfca38a226af9c
```



Signing Secret

```
8260d5411ae9d9802f1e0e4d136c9097
```



Verification Token

```
Kh4HvYmjPAbkl1zBFzJtZK35
```



Webhook URL

```
https://hooks.slack.com/services/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
```







You'll need to send this secret along with your client ID when making your [oauth.v2.access](https://api.slack.com/methods/oauth.v2.access) request.Signing Secret[ ]

Slack signs the requests we send you using this secret. Confirm that each request comes from Slack by verifying its unique signature.Verification Token[ ]

This deprecated Verification Token can still be used to verify that requests come from Slack, but we strongly recommend using the above, more secure, signing secret instead.
