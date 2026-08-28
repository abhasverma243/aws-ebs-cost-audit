import boto3

# -----------------------------
# Configuration
# -----------------------------

REGION = "ap-southeast-2"
EBS_COST_PER_GB_MONTH = 0.08


# -----------------------------
# AWS Client
# -----------------------------

ec2 = boto3.client("ec2", region_name=REGION)


# -----------------------------
# Discovery
# -----------------------------

def get_volumes():
    """Retrieve all EBS volumes from AWS."""

    volumes = []

    paginator = ec2.get_paginator("describe_volumes")

    for page in paginator.paginate():
        volumes.extend(page["Volumes"])

    return volumes


def get_snapshots():
    """Retrieve all EBS snapshots owned by this account."""

    snapshots = []

    paginator = ec2.get_paginator("describe_snapshots")

    for page in paginator.paginate(
        OwnerIds=["self"]
    ):
        snapshots.extend(page["Snapshots"])

    return snapshots


# -----------------------------
# Main
# -----------------------------

def main():

    volumes = get_volumes()
    snapshots = get_snapshots()

    print("AWS EBS COST AUDIT")
    print("----------------------------")

    print(f"Volumes found: {len(volumes)}")
    print(f"Snapshots found: {len(snapshots)}")


if __name__ == "__main__":
    main()
