"""
Utility functions for Scraparr API interactions.

This module contains helper functions to avoid duplicate code.
"""

import logging
import requests


def get(api_url, api_key):
    """Get data from API and Logs errors"""
    try:
        r = requests.get(api_url, headers={"X-Api-Key": api_key}, timeout=20)
        if r.status_code == 200:
            return r.json()

        logging.error("Error: %s", r.status_code)
    except requests.exceptions.RequestException as e:
        logging.error("Error: %s", e)
    return {}


def update_status(status, root_folder, status_labels):
    """Update the Status"""
    if status in status_labels:
        status_labels[status]["paths"]["total"] += 1
        status_labels[status]["paths"][root_folder] += 1


def update_genre_count(genres, genre_count, root_folder):
    """Update the Genre Count"""
    for genre in genres:
        if genre not in genre_count:
            genre_count[genre] = {"total": 0, root_folder: 0}
        elif root_folder not in genre_count[genre]:
            genre_count[genre][root_folder] = 0
        genre_count[genre]["total"] += 1
        genre_count[genre][root_folder] += 1


def increase_quality_count(quality_count, files, path):
    """Increase the Quality Count"""
    for file in files:
        quality = file['quality']['quality']['name']
        if quality not in quality_count:
            quality_count[quality] = {"total": 0, path: 0}
        elif path not in quality_count[quality]:
            quality_count[quality][path] = 0

        quality_count[quality]["total"] += 1
        quality_count[quality][path] += 1


def update_monitoring(media, data, alias):
    """Update the Media Monitoring"""

    title, root_folder, detailed, missing_metrics = data

    if media[0]["monitored"]:
        if not media[0]["hasFile"]:
            media[2]["missing"][0] += 1
            media[1]["missing"]["paths"][root_folder] += 1
            if detailed:
                missing_metrics.labels(alias, title).set(1)

        media[2]["monitored"][0] += 1
        media[1]["monitored"]["paths"][root_folder] += 1
    else:
        media[2]["unmonitored"][0] += 1
        media[1]["unmonitored"]["paths"][root_folder] += 1


def update_count(size, root_folder, media_count, status_labels, sonarr=None):
    """Update the Media Count"""
    if root_folder not in media_count["total"]["paths"]:
        media_count["total"]["paths"][root_folder] = 0
        media_count["missing"]["paths"][root_folder] = 0
        media_count["monitored"]["paths"][root_folder] = 0
        media_count["unmonitored"]["paths"][root_folder] = 0
        if sonarr:
            media_count["episode"]["paths"][root_folder] = 0
        size[1][root_folder] = 0
        for status in status_labels:
            status_labels[status]["paths"][root_folder] = 0

    media_count["total"]["paths"][root_folder] += 1

    if sonarr:
        sonarr[1]["episode"][0] += sonarr[0]
        media_count["episode"]["paths"][root_folder] += sonarr[0]
    size[1]['total'] += size[0]
    size[1][root_folder] += size[0]


def status_update(status_list, alias):
    """Update the Status"""
    for status in status_list:
        for path, value in status_list[status]["paths"].items():
            if path == "total":
                status_list[status]["func"][1].labels(alias).set(value)
            else:
                status_list[status]["func"][0].labels(alias, path).set(value)

def total_with_label(data, alias):
    """Get the total count with label"""
    for label, paths in data[0].items():
        for path, count in paths.items():
            if path == "total":
                data[2].labels(alias, label).set(count)
            else:
                data[1].labels(alias, label, path).set(count)

def update_media_metrics(media, alias):
    """Update the Media Metrics"""

    quality_data, used_size, genre_count, status_labels, media_count = media

    total_with_label(quality_data, alias)
    total_with_label(genre_count, alias)

    for status in media_count["path"]:
        for path, count in media_count["path"][status]["paths"].items():
            media_count["path"][status]["func"].labels(alias, path).set(count)
    for status in media_count["total"]:
        media_count["total"][status][1].labels(alias).set(media_count["total"][status][0])

    for path, size in used_size[0].items():
        if path == "total":
            used_size[2].labels(alias).set(size)
        else:
            used_size[1].labels(alias, path).set(size)

    status_update(status_labels, alias)
