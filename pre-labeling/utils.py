import os
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import json
import boto3
from urllib.parse import urlparse
from datetime import datetime            


#List of coco labels
coco_labels= ["person",
"bicycle",
"car",
"motorcycle",
"airplane",
"bus",
"train",
"truck",
"boat",
"traffic light",
"fire hydrant",
"stop sign",
"parking meter",
"bench",
"bird",
"cat",
"dog",
"horse",
"sheep",
"cow",
"elephant",
"bear",
"zebra",
"giraffe",
"backpack",
"umbrella",
"handbag",
"tie",
"suitcase",
"frisbee",
"skis",
"snowboard",
"sports ball",
"kite",
"baseball bat",
"baseball glove",
"skateboard",
"surfboard",
"tennis racket",
"bottle",
"wine glass",
"cup",
"fork",
"knife",
"spoon",
"bowl",
"banana",
"apple",
"sandwich",
"orange",
"broccoli",
"carrot",
"hot dog",
"pizza",
"donut",
"cake",
"chair",
"couch",
"potted plant",
"bed",
"dining table",
"toilet",
"tv",
"laptop",
"mouse",
"remote",
"keyboard",
"cell phone",
"microwave",
"oven",
"toaster",
"sink",
"refrigerator",
"book",
"clock",
"vase",
"scissors",
"teddy bear",
"hair drier",
"toothbrush"]


def get_bucket_key(s3_uri):
    
    """Returns bucket name and object key for a given s3 uri
    
    Parameters
    ----------
    s3_uri : str
    input s3 uri

    Returns
    -------
    str, str Buket name & object key
    """
  
    p = urlparse(s3_uri, allow_fragments=False)
    return p.netloc, p.path.lstrip('/')

def upload_image(sm_session,input_location,bucket,prefix= "asyncinference/input"):
    return sm_session.upload_data(
        input_location,
        bucket,
        key_prefix=prefix,
        extra_args={
            "ContentType": "application/x-image",
        },
    )


def upload_file(sm_session,input_location,bucket,prefix=None):
    
    if prefix != None:
        return sm_session.upload_data(input_location, bucket,key_prefix=prefix)
    else:
        return sm_session.upload_data(input_location, bucket)

def plot_bbox(
    img,
    bboxes,
    scores=None,
    labels=None,
    thresh=0.5,
    class_names=None,
    colors=None,
    ax=None,
    linewidth=3.5,
    fontsize=12,
):
    """Plot box over the predicted objects."""

    from matplotlib import pyplot as plt
    import random

    img = img.copy()
    ax.imshow(img.astype(np.uint8))

    colors = dict()

    for i, bbox in enumerate(bboxes):
        if scores.flat[i] < thresh or labels.flat[i] < 0:
            continue
        cls_id = int(labels.flat[i]) if labels is not None else -1
        if cls_id not in colors:
            if class_names is not None:
                colors[cls_id] = plt.get_cmap("hsv")(cls_id / len(class_names))
            else:
                colors[cls_id] = (random.random(), random.random(), random.random())
        xmin, ymin, xmax, ymax = [int(x) for x in bbox]
        rect = plt.Rectangle(
            (xmin, ymin),
            xmax - xmin,
            ymax - ymin,
            fill=False,
            edgecolor=colors[cls_id],
            linewidth=linewidth,
        )
        ax.add_patch(rect)
        if class_names is not None and cls_id < len(class_names):
            class_name = class_names[cls_id]
        else:
            class_name = str(cls_id) if cls_id >= 0 else ""
        score = "{:.3f}".format(scores.flat[i]) if scores is not None else ""
        if class_name or score:
            ax.text(
                xmin,
                ymin - 2,
                "{:s} {:s}".format(class_name, score),
                bbox=dict(facecolor=colors[cls_id], alpha=0.5),
                fontsize=fontsize,
                color="white",
            )
    return ax



def parse_response(response_object):
   
    """Parse response and return a set of bounding boxes, masks, class names and scores for predictions along with the original image overlaid with the mask.
    
    Parameters
    ----------
    response_object : str(json string) or dict 

    Returns
    -------
    nparray ids, scorex, boundingboxes, image with mask, width, height
    """
    
    
    if type(response_object) == dict:
        response_dict = response_object
    else:
        response_dict = json.loads(response_object)
    
    ids,scores,bboxes,masks,image_with_masks  = (np.array(response_dict["ids"]),
                                                 np.array(response_dict["scores"]),
                                                 np.array(response_dict["bboxes"]),
                                                 np.array(response_dict["masks"]),
                                                 np.array(response_dict["image_with_masks"]))
    
    width, height = image_with_masks.shape[1], image_with_masks.shape[0]
    
    return (
         ids,scores,bboxes,masks,image_with_masks,width,height
    )



def plot_response (response_object,figsize=(20, 20)):
    
    """Plots the response object
    
    Parameters
    ----------
    response_object : str- Model prediction file name

    """
    json_dict = json.load(open(response_object))
    ids, scores, bboxes, masks, image_with_masks,width,height = parse_response(json_dict)
    fig = plt.figure(figsize=(20, 20))
    ax = fig.add_subplot(1, 1, 1)
    ax = plot_bbox(image_with_masks, bboxes,scores, ids, ax=ax,class_names=coco_labels)
    plt.show()


def sm_gt_manifest_jsonl(source_image,ids,scores,bboxes,width,height,depth=3,bbox_attr_name="prelabel",labels = coco_labels):
    _scores = scores.flat
    _ids = ids.flat
    
    bbox_attr_name_metadata = bbox_attr_name + "-metadata"
    create_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
    resp = {"source-ref":source_image}
    resp[bbox_attr_name] = {"annotations":[], "image_size":[]}
    resp[bbox_attr_name_metadata] = {"job-name":"adas-pre-labeling-job", 
                                     "class-map":{}, 
                                     "human-annotated": "no", 
                                     "objects": [],
                                     "type": "groundtruth/object-detection",
                                     "creation-date": create_date
                                    }
    
    
    resp[bbox_attr_name]["image_size"].append({"width":width,"height":height,"depth":depth})
    
    for i, bbox in enumerate(bboxes):
        xmin, ymin, xmax, ymax = [int(x) for x in bbox]
        w = xmax - xmin
        h = ymax - ymin
        top = ymin
        left = xmin
        class_id = int(_ids[i])
        resp[bbox_attr_name]["annotations"].append({"class_id": class_id, "width":w, "height":h,"top":top,"left":left})
        resp[bbox_attr_name_metadata]["objects"].append({"confidence":_scores[i]})
        resp[bbox_attr_name_metadata]["class-map"][class_id] = labels[class_id]
    
    return json.dumps(resp)
    
def convert_to_sm_gt_manifest(output_locations,image_bucket,image_prefix,manifest_file_name="annotations.manifest"):
    s3_client = boto3.client('s3')

    with open(manifest_file_name, "w") as outfile:
        for i in range(len(output_locations)):
            file_name = "data/predictions/annotation-" + str(i) + ".out"
            image_file_name = "image-" + str(i) + ".png"
            image_file_path = "data/segmentation/" + image_file_name
            bucket,key = get_bucket_key(output_locations[i])
            print(f'Downloading file {key} from bucket {bucket}')
            s3_client.download_file(bucket, key, file_name)
            json_dict = json.load(open(file_name))
            ids, scores, bboxes, masks, image_with_masks,width, height  =parse_response(json_dict)
            mpimg.imsave(image_file_path, image_with_masks.astype(np.uint8))
            s3_client.upload_file(image_file_path, image_bucket, image_prefix + "/" + image_file_name)
            s3_image_uri = f"s3://{image_bucket}/{image_prefix}/{image_file_name}"
            jsonl = sm_gt_manifest_jsonl(s3_image_uri,ids,scores,bboxes,width, height ) + "\n"
            outfile.write(jsonl)
            
    print(f'done. Manifest file generated {manifest_file_name}')
    
def upload__gt_template(template_bucket,template_prefix,template_name='instrunctions.template'):
    s3_client = boto3.client('s3')
    s3_client.upload_file(template_name, template_bucket, template_prefix + "/" + template_name)