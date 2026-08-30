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

def analyze_volumes(volumes):
    """Identify potentially wasteful EBS volumes."""

    findings = []

    for volume in volumes:

        if volume["State"] == "available":

            volume_id = volume["VolumeId"]
            size = volume["Size"]

            estimated_cost = size * EBS_COST_PER_GB_MONTH

            findings.append({
                "resource_type": "EBS Volume",
                "resource_id": volume_id,
                "reason": "Unattached",
                "size_gb": size,
                "estimated_monthly_cost": estimated_cost
            })

    return findings

def analyze_snapshots(snapshots, volume_ids):
    """Identify potentially orphaned EBS snapshots."""

    findings = []

    for snapshot in snapshots:

        snapshot_id = snapshot["SnapshotId"]
        size = snapshot["VolumeSize"]
        source_volume = snapshot.get("VolumeId")

        if source_volume not in volume_ids:

            estimated_cost = size * EBS_COST_PER_GB_MONTH

            findings.append({
                "resource_type": "EBS Snapshot",
                "resource_id": snapshot_id,
                "reason": "Source volume missing",
                "size_gb": size,
                "estimated_monthly_cost": estimated_cost
            })

    return findings




# -----------------------------
# Main
# -----------------------------
def main():

    volumes = get_volumes()
    snapshots = get_snapshots()
    volume_ids = {
        volume["VolumeId"]
        for volume in volumes
    }



    volume_findings = analyze_volumes(volumes)
    snapshot_findings = analyze_snapshots(
        snapshots,
        volume_ids
    )

    print("AWS EBS COST AUDIT")
    print("----------------------------")

    print(f"Volumes found: {len(volumes)}")
    print(f"Snapshots found: {len(snapshots)}")

    print("\nVolume Findings:")

    for finding in volume_findings:
        print(finding)

    print("\nSnapshot Findings:")

    for finding in snapshot_findings:
        print(finding)



if __name__ == "__main__":
    main()
