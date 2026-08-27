import boto3

ec2 = boto3.client("ec2", region_name="ap-southeast-2")

response = ec2.describe_volumes()

existing_volume_ids = set()

print("EBS Cost Audit")
print("----------------------------")

print("\nVolumes:")

for volume in response["Volumes"]:
    volume_id = volume["VolumeId"]
    size = volume["Size"]
    state = volume["State"]

    existing_volume_ids.add(volume_id)

    if state == "available":
        status = "unattached"
    else:
        status = "attached"

    print(f"{volume_id}    {size} GB    {status}")


snapshot_response = ec2.describe_snapshots(
    OwnerIds=["self"]
)

print("\nSnapshots:")

for snapshot in snapshot_response["Snapshots"]:
    snapshot_id = snapshot["SnapshotId"]
    size = snapshot["VolumeSize"]
    source_volume = snapshot["VolumeId"]

    if source_volume in existing_volume_ids:
        status = "source volume exists"
    else:
        status = "source volume missing"

    print(f"{snapshot_id}    {size} GB    {status}")
