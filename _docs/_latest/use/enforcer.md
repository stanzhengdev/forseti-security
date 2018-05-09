---
title: Enforcer
order: 002
---

# {{ page.title }}

This page describes how to get started with Forseti Enforcer. Enforcer
compares policy files that define the desired state of a resource
against the current state of the resource. If it finds any differences in
policy, Enforcer makes changes using Google Cloud APIs.

Enforcer code currently supports Compute Engine firewall rules.
Additional enforcement endpoints are in development.

## Before you begin

Enforcer requires write permissions for the resources that it manages.
If you use the default Compute Engine service account, the account must have
the following permissions:

  - Permissions to update the Compute Engine API for the projects it enforces.
  - The Compute Security Admin role in your organization's Cloud IAM settings.
  - Access to the Compute Engine API scope on the instance that's running Enforcer.

You'll also need the project ID of the resource you want to enforce.

## Using Enforcer
To use Enforcer, you'll define policies in a JSON formatted rule list,
and then run Enforcer from a local or Cloud Storage policy file.

### Defining policies

Enforcer policy files are JSON formatted rule lists that apply to a
project. Each rule must contain a name, sourceRanges or sourceTags, and one or
more allowed protocols. To learn more, refer to the
[Compute Engine Firewall](https://cloud.google.com/compute/docs/reference/latest/firewalls)
documentation.

If a rule does not include a network name, then it's applied to all networks
configured on the project. The network name is prepended to the rule name.

The following is an example firewall rule (which can be applied by enforcer) that only allows:
  * SSH from anywhere
  * HTTP(S) traffic from both load balancer and health checker to VM instances
  * Only internal TCP, UDP, and ICMP traffic

  ```json
  [{
        "sourceRanges": ["0.0.0.0/0"],
        "description": "Allow SSH from anywhere",
        "allowed": [
            {
                "IPProtocol": "tcp",
                "ports": ["22"]
            }
        ],
        "name": "allow-ssh"
   },
   {
        "sourceRanges": ["130.211.0.0/22", "35.191.0.0/16"],
        "description": "Allow traffic from load balancer and health checker to reach VM instances",
        "allowed": [
            {
                "IPProtocol": "tcp",
                "ports": ["80","443"]
            }
        ],
        "name": "allow-load-balancer-and-health-checker"
   },
   {
        "sourceRanges": ["10.128.0.0/9"],
        "description": "Allow internal only",
        "allowed": [
            {
                "IPProtocol": "tcp",
                "ports": ["0-65535"]
            },
            {
                "IPProtocol": "udp",
                "ports": ["0-65535"]
            },
            {
                "IPProtocol": "icmp"
            }
        ],
        "name": "default-allow-internal"
  }]
  ```

### Running Enforcer

#### Use a local policy file

To run Enforcer with a local policy file, run the following command:

  ```bash
  $ forseti_enforcer --enforce_project PROJECT_ID \
      --policy_file path/to/policy.json
  ```

#### Use a Cloud Storage policy file

To run Enforcer with a policy file stored in Cloud Storage,
such as `gs://my-project-id/firewall-policies/default.json`, run the following
command:

  ```bash
  $ forseti_enforcer --enforce_project PROJECT_ID \
      --policy_file gs://my-project-id/firewall-policies/default.json
  ```