import boto3

def detect_labels(photo, bucket):

    client=boto3.client('rekognition', region_name='us-east-2')

    response = client.detect_labels(Image={'S3Object':{'Bucket':'projecttest-106490371129-us-east-2-an','Name':'MV5BMWQzYjY3MjEtOGEzMC00YTJjLWI0ZmEtZGQwNDVhNWQ0YTVjXkEyXkFqcGdeQXVyMTE5NDQ1MzQ3._V1_.jpg'}},
        MaxLabels=10)

    print('Detected labels for ' + photo) 
    print()   
    for label in response['Labels']:
        print ("Label: " + label['Name'])
        print ("Confidence: " + str(label['Confidence']))
        print ("Instances:")
        for instance in label['Instances']:
            print ("  Bounding box")
            print ("    Top: " + str(instance['BoundingBox']['Top']))
            print ("    Left: " + str(instance['BoundingBox']['Left']))
            print ("    Width: " +  str(instance['BoundingBox']['Width']))
            print ("    Height: " +  str(instance['BoundingBox']['Height']))
            print ("  Confidence: " + str(instance['Confidence']))
            print()

        print ("Parents:")
        for parent in label['Parents']:
            print ("   " + parent['Name'])
        print ("----------")
        print ()
    return len(response['Labels'])


def main():
    photo=''
    bucket=''
    label_count=detect_labels(photo, bucket)
    print("Labels detected: " + str(label_count))


if __name__ == "__main__":
    main()


