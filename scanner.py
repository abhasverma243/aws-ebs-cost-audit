import boto3

# Configuration
REGION = "ap-southeast-2"
EBS_COST_PER_GB_MONTH = 0.08

# Create EC2 client
ec2 = boto3.client("ec2", region_name=REGION)

# -----------------------------------
# Get EBS Volumes
# -----------------------------------

response = ec2.describe_volumes()

volumes = response["Volumes"]

print("EBS COST AUDIT")
print("----------------------------")

# Keep track of all existing volume IDs
volume_ids = set()

unattached_cost = 0

print("\nVolumes:")

for volume in volumes:

    volume_id = volume["VolumeId"]
    size = volume["Size"]
    state = volume["State"]

    volume_ids.add(volume_id)

    if state == "available":

        estimated_cost = size * EBS_COST_PER_GB_MONTH
        unattached_cost += estimated_cost

        print(
            f"{volume_id}   {size} GB   UNATTACHED   "
            f"~${estimated_cost:.2f}/month"
        )

    else:

        print(
            f"{volume_id}   {size} GB   ATTACHED"
        )


# -----------------------------------
# Get EBS Snapshots
# -----------------------------------

snapshot_response = ec2.describe_snapshots(
    OwnerIds=["self"]
)

snapshots = snapshot_response["Snapshots"]

orphaned_snapshot_cost = 0

print("\nSnapshots:")

for snapshot in snapshots:

    snapshot_id = snapshot["SnapshotId"]
    size = snapshot["VolumeSize"]
    source_volume = snapshot.get("VolumeId")

    estimated_cost = size * EBS_COST_PER_GB_MONTH

    if source_volume not in volume_ids:

        orphaned_snapshot_cost += estimated_cost

        print(
            f"{snapshot_id}   {size} GB   "
            f"ORPHANED   ~${estimated_cost:.2f}/month"
        )

    else:

        print(
            f"{snapshot_id}   {size} GB   "
            f"SOURCE EXISTS"
        )


# -----------------------------------
# Cost Summary
# -----------------------------------

total_cost = unattached_cost + orphaned_snapshot_cost

print("\n----------------------------")
print("COST SUMMARY")
print("----------------------------")

print(
    f"Unattached volume waste: "
    f"~${unattached_cost:.2f}/month"
)

print(
    f"Orphaned snapshot waste: "
    f"~${orphaned_snapshot_cost:.2f}/month"
)

print(
    f"Potential monthly waste: "
    f"~${total_cost:.2f}/month"
)
