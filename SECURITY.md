# Security policy

Foxbat is an **educational beta**, not a production intrusion detection or prevention product. Do not rely on it as the sole defense for any system or network.

## Reporting a vulnerability

Please avoid posting working exploit details, sensitive packet captures, or private network information in public issues. Contact the repository maintainer privately through their GitHub profile or another private contact channel they explicitly publish. No dedicated security-reporting address has been configured.

## Safe deployment

- Monitor only networks and interfaces you are authorized to inspect.
- Keep the API on `127.0.0.1`; it has no authentication and must not be exposed to untrusted networks.
- Npcap is needed for live packet capture; Windows WebView2 Runtime is needed for the desktop interface.
- Detection rules are heuristics; expect false positives and missed attacks.
- PCAPs, alerts, reports, and screenshots can contain private network information.
- The current signing certificate is self-signed. It is **not publicly trusted** and does not eliminate SmartScreen warnings. Do not install an unknown publisher's certificate into Trusted Root merely to run the app.
