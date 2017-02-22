"""
Title: Google Images Downloader
Author: Shabaz Badshah
Date: Feb 2017

A python command line tool that will download images from google image based on a query given.
Supports reading queries from a file, all operations are logged within their respective image folders
This tool was ultimately created because of Google's deprecated google images API as an alternative
"""

import time
import requests
import os
import re

# CONSTANTS
CONNECTION_TIMEOUT_AMOUNT = 10  # Timeout per request in seconds
DELAY_BETWEEN_LINK_REQUESTS = 0.1  # The time between each link request in milliseconds
IMAGES_SAVE_PARENT_FOLDER = "Downloaded Images"  # The name of the folder where all the image subfolders will be saved


def _download_page_html(url):
    """
    Returns the HTML data froma given URL
    :param url: str, the URL of the site that the HTML will be downloaded from
    :return: str, the HTML data
    """

    try:
        _request = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 "
                                                           "(KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})

        if _request.raise_for_status():
            raise TimeoutError

        return _request.text

    except TimeoutError:
        print("URL connection timeout: It took too long to get the html content from the url" + str(url) +
              "exiting program \n")
        exit(1)

    except requests.exceptions.ConnectionError:
        print("There was an error connecting to the URL, please check your internet connection, now "
              "exiting program\n")
        exit(1)

    except Exception as e:
        print("There was an error, exiting program")
        exit(1)


def _get_next_link_from_page(page):
    """
    A recursive function that finds the 'next' image link on the page
    :param page: str, the HTML data of a google image's result page
    :return: str, the link of the image AND int, the index from where the remainder of the HTML will need to be parsed
             returns "no_link" and 0 if no links were found
    """

    try:
        _thumbnail_image_start = page.find('rg_di')  # Finds the location of the meta information
        if _thumbnail_image_start == -1:  # If no links were found
            return "no_link", 0

        else:
            _image_meta_start = page.find('"class="rg_meta"')  # Gets meta information about each image
            _meta_content_start = page.find('"ou"', _image_meta_start + 1)  # The start of the meta info of the image
            # The end of the meta information for an individual image
            _image_meta_end = page.find(',"ow"', _meta_content_start + 1)

            _direct_image_link = str(page[_meta_content_start + 6: _image_meta_end - 1])  # The DRIECT LINK of the image

            # Returns the image link (left) and the remainder of the HTML (right)
            return _direct_image_link, _image_meta_end

    except AttributeError:
        print("The page could not be parsed, program is now exiting")
        exit(1)


def _get_all_links_from_page(page):
    """
    Returns a list of all the links from the HTML data given, the HTML data is from a google image's result page
    :param page: str, the HTML data of a google image's result page
    :return: list[str], a list of links containing all the links found within the HTML data
    """

    _image_links = []  # All of the links parsed from the google image's _query result page

    # Keeps calling 'get_next_link_from_page' to build up the list of all the links of images
    while len(_image_links) < _amount_download:

        _direct_image_link, _remainder_html_start_index = _get_next_link_from_page(page)

        if _direct_image_link == "no_links":
            break

        _image_links.append(_direct_image_link)
        # Controls the time between each request of a direct_image_link, also reduces strain on server
        time.sleep(DELAY_BETWEEN_LINK_REQUESTS)
        page = page[_remainder_html_start_index:]  # Moves forward through the HTML to get

    return _image_links


def _download_all_images(file_name, image_links):
    """
    Downloads all of the images from the list of links given and logs all the output in a file
    :param file_name: str, the name of the output file of the log
    :param image_links: list[str], the list of image links that will be downloaded
    """

    _images_requested = 0  # The number of the images requested

    # Opens the log for writing image meta information
    try:
        _log = open(str(_images_save_location_path) + "\\" + file_name + " - log.txt", 'a')
    except IOError:
        print("there was an error opening the _log, now exiting program")
        exit(1)

    _log.write("Total time taken: " + str(_total_grab_query_links_time) + " seconds to gather all links\n")
    _log.write("Requested all images from google images with URL: " + url + "\n")
    _log.write("Search Query: " + str(_all_user_search_queries[_current_query_number]) + "\n")

    '''Loops through the array of links and downloads the image, if an image download is failed, the next link is
       requested and the image is downloaded'''
    while _images_requested < len(image_links):

        _image_name = None  # The name of the image
        _image_ext = None  # The extension of the image

        try:
            # Gets the image's raw data from the link
            _image_data = requests.get(image_links[_images_requested], headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) "
                              "Chrome/24.0.1312.27 Safari/537.17"}, timeout=CONNECTION_TIMEOUT_AMOUNT)

            if _image_data.raise_for_status():
                raise TimeoutError
            else:

                # Regex to identify an image's name and extension, ignores all special characters
                _image_name_ext_regex = re.compile("([\w-]+)(\.(jpe?g|png|gif|bmp))", re.MULTILINE)

                # Gets the image name and extension from the URL
                _image_file_ext_name = _image_name_ext_regex.search(str(image_links[_images_requested]))

                _image_name = _image_file_ext_name[0]  # The name of the image returned from the tuple of the regex search
                _image_ext = _image_file_ext_name[2]  # The ext of the image returned from the tuple of the regex search

                _log.write("\t Image info: " + "\n")
                _log.write("\t\t Image number: " + str(_images_requested + 1) + "\n")

                '''If the name of the image >60 characters, most OS's will have problems storing that file, so it is
                skipped, but information about it is still stored'''
                if len(_image_name) > 60:
                    print("Image name was too long, it has been skipped\n")
                    _log.write("\t\t Image name: [WAS SKIPPED, IMAGE NAME TOO LONG]" + str(_image_name) + "\n")
                    _log.write("\t\t Image ext: " + str(_image_ext) + "\n")
                    _log.write("\t\t Image was requested from " + str(image_links[_images_requested]) + "\n")
                    pass
                else:
                    _log.write("\t\t Image name: " + str(_image_name) + "\n")

                _log.write("\t\t Image ext: " + str(_image_ext) + "\n")
                _log.write("\t\t Image downloaded from " + str(image_links[_images_requested]) + "\n")

                print("\t Image info: ")
                print("\t\t Image number: " + str(_images_requested + 1))
                print("\t\t Image name: " + str(_image_name))
                print("\t\t Image ext: " + str(_image_ext))
                print("\t\t Image downloaded from " + str(image_links[_images_requested]))

                # Creates the image file name and save location
                _output_file = open(str(_images_save_location_path) + "\\" + str(_images_requested + 1)
                                   + "---" + str(_image_name), 'wb')
                # Grabs the image data from the image_data received from the image link
                _data = _image_data.content
                # Saves the actual image and write it to the save location
                _output_file.write(_data)

        except TypeError:
            _log.write("\t Image info: [TYPE ERROR]" + "\n")
            _log.write("\t\t Image number: " + str(_images_requested + 1) + "\n")
            if _image_name is not None:
                _log.write("\t\t Image name: " + str(_image_name) + "\n")
            else:
                _log.write("\t\t Image name: Error getting name\n")
            if _image_ext is not None:
                _log.write("\t\t Image ext: " + str(_image_ext) + "\n")
            else:
                _log.write("\t\t Image name: Error getting ext\n")

            _log.write("\t\t Image requested from " + str(image_links[_images_requested]) + "\n")

            print("\t Image info: [IO ERROR]")
            print("\t\t Image number: " + str(_images_requested + 1))

            if _image_name is not None:
                print("\t\t Image name: " + str(_image_name))
            else:
                print("\t\t Image name: Error getting name")
            if _image_ext is not None:
                print("\t\t Image ext: " + str(_image_ext))
            else:
                print("\t\t Image ext: Error getting ext")

            print("\t\t Image requested from " + str(image_links[_images_requested]))

            _images_requested += 1
            continue

        except IOError:
            _log.write("\t Image info: [IO ERROR]" + "\n")
            _log.write("\t\t Image number: " + str(_images_requested + 1) + "\n")

            if _image_name is not None:
                _log.write("\t\t Image name: " + str(_image_name) + "\n")
            else:
                _log.write("\t\t Image name: Error getting name\n")
            if _image_ext is not None:
                _log.write("\t\t Image ext: " + str(_image_ext) + "\n")
            else:
                _log.write("\t\t Image name: Error getting ext\n")
            _log.write("\t\t Image requested from " + str(image_links[_images_requested]) + "\n")

            print("\t Image info: [IO ERROR]")
            print("\t\t Image number: " + str(_images_requested + 1))

            if _image_name is not None:
                print("\t\t Image name: " + str(_image_name))
            else:
                print("\t\t Image name: Error getting name")
            if _image_ext is not None:
                print("\t\t Image ext: " + str(_image_ext))
            else:
                print("\t\t Image ext: Error getting ext")
            print("\t\t Image requested from " + str(image_links[_images_requested]))

            _images_requested += 1
            continue

        except TimeoutError:
            _log.write("\t Image info: [TIMEOUT ERROR]" + "\n")
            _log.write("\t\t Image number: " + str(_images_requested + 1) + "\n")

            if _image_name is not None:
                _log.write("\t\t Image name: " + str(_image_name) + "\n")
            else:
                _log.write("\t\t Image name: Error getting name\n")
            if _image_ext is not None:
                _log.write("\t\t Image ext: " + str(_image_ext) + "\n")
            else:
                _log.write("\t\t Image name: Error getting ext\n")

            _log.write("\t\t Image requested from " + str(image_links[_images_requested]) + "\n")

            print("\t Image info: [TIMEOUT ERROR]")
            print("\t\t Image number: " + str(_images_requested + 1))

            if _image_name is not None:
                print("\t\t Image name: " + str(_image_name))
            else:
                print("\t\t Image name: Error getting name")
            if _image_ext is not None:
                print("\t\t Image ext: " + str(_image_ext))
            else:
                print("\t\t Image ext: Error getting ext")

            print("\t\t Image requested from " + str(image_links[_images_requested]))

            _images_requested += 1
            continue

        except IndexError:
            _log.write("\t Image info: [INDEX ERROR]" + "\n")
            _log.write("\t\t Image number: " + str(_images_requested + 1) + "\n")

            if _image_name is not None:
                _log.write("\t\t Image name: " + str(_image_name) + "\n")
            else:
                _log.write("\t\t Image name: Error getting name\n")
            if _image_ext is not None:
                _log.write("\t\t Image ext: " + str(_image_ext) + "\n")
            else:
                _log.write("\t\t Image name: Error getting ext\n")

            _log.write("\t\t Image requested from " + str(image_links[_images_requested]) + "\n")
            _images_requested += 1

            print("\t Image info: [INDEX ERROR]")
            print("\t\t Image number: " + str(_images_requested + 1))
            if _image_name is not None:
                print("\t\t Image name: " + str(_image_name))
            else:
                print("\t\t Image name: Error getting name")
            if _image_ext is not None:
                print("\t\t Image ext: " + str(_image_ext))
            else:
                print("\t\t Image ext: Error getting ext")
            print("\t\t Image requested from " + str(image_links[_images_requested]))

            continue

        except Exception:
            _log.write("\t Image info: [GENERIC ERROR]" + "\n")
            _log.write("\t\t Image number: " + str(_images_requested + 1) + "\n")

            if _image_name is not None:
                _log.write("\t\t Image name: " + str(_image_name) + "\n")
            else:
                _log.write("\t\t Image name: Error getting name\n")
            if _image_ext is not None:
                _log.write("\t\t Image ext: " + str(_image_ext) + "\n")
            else:
                _log.write("\t\t Image name: Error getting ext\n")

            _log.write("\t\t Image requested from " + str(image_links[_images_requested]) + "\n")
            _images_requested += 1

            print("\t Image info: [INDEX ERROR]")
            print("\t\t Image number: " + str(_images_requested + 1))
            if _image_name is not None:
                print("\t\t Image name: " + str(_image_name))
            else:
                print("\t\t Image name: Error getting name")
            if _image_ext is not None:
                print("\t\t Image ext: " + str(_image_ext))
            else:
                print("\t\t Image ext: Error getting ext")
            print("\t\t Image requested from " + str(image_links[_images_requested]))

            continue

        _images_requested += 1

    _log.close()

if __name__ == "__main__":

    _all_user_search_queries = []  # The list of all the queries given by the user/file

    _empty_file = True  # A boolean used to indicate an empty log
    _load_from_file = None # A boolean to indicate that the user will load from a file

    '''Loads queries from a txt file if provided, each query is separated by a \n character
       if an error occurs, the program will switch to manual input from the user'''
    if os.path.exists(str("words.txt")):
        try:
            _load_from_file = True

            _search_file = open(str(os.path._getfullpathname("words.txt")), 'r')

            print("Loading queries from file\n")

            for word in _search_file:
                _all_user_search_queries.append(str(word))

            if len(_all_user_search_queries) == 0:
                print("The log was empty, program is now switching to manual input\n")
            else:
                print("Done loading queries from file\n")
                _empty_file = False

        except IOError:
            print("There was an error loading from the file, program is now switching to "
                  "manual input\n")
            _load_from_file = False

    if _empty_file or not _load_from_file:
        # Gets all the queries from the user
        while True:
            _query = input("Enter in the queries you want to download. Press enter to move to the next _query and "
                           "'go' to start downloading \n")

            if str(_query).lower() == "go":
                break
            else:
                _all_user_search_queries.append(str(_query))

    # Gets the amount of images to download for all queries
    while True:
        try:
            _amount_download = input("Enter in the amount of images you would like to download between 1 and 100\n")

        except ValueError:
            print("Enter in a valid number between 1 and 100\n")

        if str(_amount_download).isnumeric() and (int(_amount_download) in range(1 , 101)):
            break

    _amount_download = int(_amount_download)  # The amount of images to download (1 < amount <= 100)

    '''
    The regex used to identify a valid folder name
        Matches all of the following characters (this expression is reversed when finding valid folder names)
            OR, *, -, ", /, \, :, ?, |, ., site:, related:, #, @, $, %, filetype:
    '''
    _folder_name_regex = re.compile(r"-\w*|OR|\*|\"|-|/|\\|:|\$|%|\?|\||\w*\.\w*|filetype:|site:|related:|#\w*|@\w*",
                                    re.MULTILINE)

    _folder_names = []  # The names of all the folders created for all the queries

    ''' Removes all special terms from google _current_query _query and then removes all the additional whitespace
        between character '''
    for i in range(len(_all_user_search_queries)):
        ''' Replaces all the special terms with '', removes all of Google special search modifier syntax
            Google Search Syntax: https://support.google.com/websearch/answer/2466433?hl=en'''
        _individual_search_terms = re.sub(_folder_name_regex, '', _all_user_search_queries[i]).strip(' ')

        # Fins all the words from the current _query and makes those set of words the folder name
        _folder_names.append(' '.join(re.findall(r"\w+", _individual_search_terms, re.MULTILINE)))

    try:
        '''Creates a subdirectory to store all of the downloaded images folders, then switches to that folder to make
           it the new working directory for the paths'''
        if not os.path.isdir(IMAGES_SAVE_PARENT_FOLDER):
            os.makedirs(IMAGES_SAVE_PARENT_FOLDER)
            os.chdir(IMAGES_SAVE_PARENT_FOLDER)
        else:
            os.chdir(IMAGES_SAVE_PARENT_FOLDER)
    except IOError:
        print("There was an error creating the 'Download_Images' save location, program is now exiting")
        exit(1)

    _current_query_number = 0  # The current _query being worked on from the _all_user_search_queries list

    # Loops through the _all_user_search_queries list and downloads their respective images
    while _current_query_number < len(_all_user_search_queries):

        _query_all_image_links = []  # Links of all the images in the page

        # Checks to see if the folder of the images already exists, creates a folder for each _query
        if not os.path.isdir(_folder_names[_current_query_number]):
            try:

                ''' Makes sure folder name length conforms to less that 60 characters, otherwise OS's have
                    problems with them '''
                if len(_folder_names[_current_query_number]) > 60:
                    # Grabs 250 characters from the initial name
                    _revised_file_name = _folder_names[_current_query_number][0:60]
                    os.makedirs(_revised_file_name)
                else:
                    os.makedirs(_folder_names[_current_query_number])
            except IOError:
                print("There was a problem creating the directory, moving onto next _query")
                continue
            except IndexError:
                print("There was a problem with the directory file name, moving onto next _query")
                continue

        # The location where each _query's respective images will be saved
        _images_save_location_path = str(os.path._getfullpathname(_folder_names[_current_query_number]))

        _grab_query_links_time_start = time.time()  # The start time of how long it took to grab all _query image links

        print("Evaluating _query: " + _folder_names[_current_query_number])

        ''' %20, the 20 is ASCII for a space character, the % allows it to be used within the URL which
            would not be usually allowed '''
        _current_query = _all_user_search_queries[_current_query_number].replace(' ', '%20')

        limit_to_week = "&as_qdr=w"  # Limits the _current_query results to ones from past week only
        safe_search = "&safe=active"  # Turns on Google's safe _current_query feature to filter out explicit content
        # The google images page of the requested _query, the '&tbm=isch' explicitly loads the _query's result page
        url = 'https://www.google.com/search?q=' + _current_query + '&tbm=isch'
        _raw_html = (_download_page_html(url))

        # Gets all the links of images on the google image's page
        _query_all_image_links += _get_all_links_from_page(_raw_html)

        # If google does not have any images for the _query
        if _query_all_image_links[0][0:4] == "type":
            print("Google could not process your _query, moving to next _query")
            _current_query_number += 1
            continue

        _grab_query_links_time_end = time.time()  # The end time of how long it took to grab all _query image links
        _total_grab_query_links_time = _grab_query_links_time_end - _grab_query_links_time_start
        print("Total time taken: " + str(_total_grab_query_links_time) + " seconds")

        print("Starting download for _query: " + _folder_names[_current_query_number])

        if len(_query_all_image_links) == 0:
            print("All queries were skipped because google could not process them")
            continue
        else:
            # Downloads all images from their respective links
            _download_all_images(_folder_names[_current_query_number], _query_all_image_links)

        _current_query_number += 1

    print("\nFinished downloading all images, check individual logs for more info")
