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


def update_monitoring(media, title, root_folder, detailed, missing_metrics):
    """Update the Media Monitoring"""

    if media[0]["monitored"]:
        if not media[0]["hasFile"]:
            media[1]["missing"]["paths"]["total"] += 1
            media[1]["missing"]["paths"][root_folder] += 1
            if detailed:
                missing_metrics.labels(title).set(1)

        media[1]["monitored"]["paths"]["total"] += 1
        media[1]["monitored"]["paths"][root_folder] += 1
    else:
        media[1]["unmonitored"]["paths"]["total"] += 1
        media[1]["unmonitored"]["paths"][root_folder] += 1


def update_count(size, root_folder, media_count, status_labels, episode_count=-1):
    """Update the Media Count"""
    if root_folder not in media_count["total"]["paths"]:
        media_count["total"]["paths"][root_folder] = 0
        media_count["missing"]["paths"][root_folder] = 0
        media_count["monitored"]["paths"][root_folder] = 0
        media_count["unmonitored"]["paths"][root_folder] = 0
        if episode_count != -1:
            media_count["episode"]["paths"][root_folder] = 0
        size[1][root_folder] = 0
        for status in status_labels:
            status_labels[status]["paths"][root_folder] = 0

    media_count["total"]["paths"][root_folder] += 1

    if episode_count != -1:
        media_count["episode"]["paths"]["total"] += episode_count
        media_count["episode"]["paths"][root_folder] += episode_count
    size[1]['total'] += size[0]
    size[1][root_folder] += size[0]


def update_media_metrics(quality_data, used_size, genre_count, status_labels, media_count):
    """Update the Media Metrics"""

    for quality, paths in quality_data[0].items():
        for path, count in paths.items():
            quality_data[1].labels(quality, path).set(count)

    for status in media_count:
        for path, count in media_count[status]["paths"].items():
            media_count[status]["func"].labels(path).set(count)

    for path, size in used_size[0].items():
        used_size[1].labels(path).set(size)

    for status in status_labels:
        for path, value in status_labels[status]["paths"].items():
            status_labels[status]["func"].labels(path).set(value)

    for genre, paths in genre_count[0].items():
        for path, count in paths.items():
            genre_count[1].labels(genre, path).set(count)
