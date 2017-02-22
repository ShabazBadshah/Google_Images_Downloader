'''
Title: Google Images Downloader
Author: Shabaz Badshah
Date: Feb 2017

A python command line tool that will download images from google image based on a query given.
Supports reading queries from a file, all operations are logged within their respective image folders
This tool was ultimately created because of Google's deprecated google images API as an alternative
'''

import time
import requests
import os
import re
import wikipedia

# CONSTANTS
CONNECTION_TIMEOUT_AMOUNT = 10  # Timeout per request in seconds
DELAY_BETWEEN_LINK_REQUESTS = 0.1  # The time between each link request in milliseconds


def _download_page_html(url):
    """
    Returns the HTML data froma given URL
    :param url: str, the URL of the site that the HTML will be downloaded from
    :return: str, the HTML data
    """

    try:
        request = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})

        if request.raise_for_status():
            raise TimeoutError

        return request.text

    except TimeoutError:
        print("URL connection timeout: It took too long to get the html content from the url" + str(url) + "exiting program \n")
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
        thumbnail_image_start = page.find('rg_di')  # Finds the location of the meta information
        if thumbnail_image_start == -1:  # If no links were found
            return "no_link", 0

        else:
            image_meta_start = page.find('"class="rg_meta"')  # Gets meta information about each image
            meta_content_start = page.find('"ou"', image_meta_start + 1)  # The start of the meta info of the image
            # The end of the meta information for an individual image
            image_meta_end = page.find(',"ow"', meta_content_start + 1)

            direct_image_link = str(page[meta_content_start + 6 : image_meta_end - 1]) # The DRIECT LINK of the image

            # Returns the image link (left) and the remainder of the HTML (right)
            return direct_image_link, image_meta_end

    except AttributeError:
        print("The page could not be parsed, program is now exiting")
        exit(1)


def _get_all_links_from_page(page):
    """
    Returns a list of all the links from the HTML data given, the HTML data is from a google image's result page
    :param page: str, the HTML data of a google image's result page
    :return: list[str], a list of links containing all the links found within the HTML data
    """

    image_links = []  # All of the links parsed from the google image's query result page

    # Keeps calling 'get_next_link_from_page' to build up the list of all the links of images
    while len(image_links) < amount_download:

        direct_image_link, remainder_html = _get_next_link_from_page(page)

        if direct_image_link == "no_links":
            break

        image_links.append(direct_image_link)
        # Controls the time between each request of a direct_image_link, also reduces strain on server
        time.sleep(DELAY_BETWEEN_LINK_REQUESTS)
        page = page[remainder_html:]  # Moves forward through the HTML to get

    return image_links


def _download_all_images(file_name, image_links):
    """
    Downloads all of the images from the list of links given and logs all the output in a file
    :param file_name: str, the name of the output file of the log
    :param image_links: list[str], the list of image links that will be downloaded
    """

    images_requested = 0  # The number of the images requested

    # Opens the log for writing image meta information
    try:
        log = open(str(images_save_location_path) + "\\" + file_name + " - log.txt", 'a')  # Open the text file called database.txt
    # log.write(all_user_search_queries + ": " + str(query_all_image_links) + "\n\n\n")         #Write the title of the page
    except IOError:
        print("there was an error opening the log, now exiting program")
        exit(1)

    log.write("Starting Download-----")
    log.write("Total time taken: " + str(total_grab_query_links_time) + " seconds to gather all links\n")
    log.write("Requested all images from google images with URL: " + url + "\n")
    log.write("Search Query: " + str(all_user_search_queries[current_query_number]) + "\n")

    '''Loops through the array of links and downloads the image, if an image download is failed, the next link is
       requested and the image is downloaded'''
    while images_requested < len(image_links):

        image_name = None  # The name of the image
        image_ext = None  # The extension of the image

        try:
            # Gets the image's raw data from the link
            image_data = requests.get(image_links[images_requested], headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) "
                              "Chrome/24.0.1312.27 Safari/537.17"}, timeout=CONNECTION_TIMEOUT_AMOUNT)

            if image_data.raise_for_status():
                raise TimeoutError
            else:

                # Regex to identify an image's name and extension, ignores all special characters
                image_name_ext_regex = re.compile("([\w-]+)(\.(jpe?g|png|gif|bmp))", re.MULTILINE)

                # Gets the image name and extension from the URL
                image_file_ext_name = image_name_ext_regex.search(str(image_links[images_requested]))

                image_name = image_file_ext_name[0]  # The name of the image returned from the tuple of the regex search
                image_ext = image_file_ext_name[2]  # The ext of the image returned from the tuple of the regex search

                log.write("\t Image info: " + "\n")
                log.write("\t\t Image number: " + str(images_requested + 1) + "\n")

                if len(image_name) > 60:
                    print("Image name was too long, it has been shortened")
                    image_name = image_name[0:60]
                    log.write("\t\t Image name: [WAS SHORTENED]" + str(image_name) + "\n")
                else:
                    log.write("\t\t Image name: " + str(image_name) + "\n")

                log.write("\t\t Image ext: " + str(image_ext) + "\n")
                log.write("\t\t Image downloaded from " + str(image_links[images_requested]) + "\n")

                print("\t Image info: ")
                print("\t\t Image number: " + str(images_requested + 1))
                print("\t\t Image name: " + str(image_name))
                print("\t\t Image ext: " + str(image_ext))
                print("\t\t Image downloaded from " + str(image_links[images_requested]))

                # Creates the image file name and save location
                output_file = open(str(images_save_location_path) + "\\" + str(images_requested + 1)
                                   + "_" + str(image_name), 'wb')
                # Grabs the image data from the image_data received from the image link
                data = image_data.content
                # Saves the actual image and write it to the save location
                output_file.write(data)

        except TypeError:
            log.write("\t Image info: [TYPE ERROR]" + "\n")
            log.write("\t\t Image number: " + str(images_requested + 1) + "\n")
            if image_name is not None:
                log.write("\t\t Image name: " + str(image_name) + "\n")
            else:
                log.write("\t\t Image name: Error getting name\n")
            if image_ext is not None:
                log.write("\t\t Image ext: " + str(image_ext) + "\n")
            else:
                log.write("\t\t Image name: Error getting ext\n")

            log.write("\t\t Image requested from " + str(image_links[images_requested]) + "\n")

            print("\t Image info: [IO ERROR]")
            print("\t\t Image number: " + str(images_requested + 1))

            if image_name is not None:
                print("\t\t Image name: " + str(image_name))
            else:
                print("\t\t Image name: Error getting name")
            if image_ext is not None:
                print("\t\t Image ext: " + str(image_ext))
            else:
                print("\t\t Image ext: Error getting ext")

            print("\t\t Image requested from " + str(image_links[images_requested]))

            images_requested += 1
            continue

        except IOError:
            log.write("\t Image info: [IO ERROR]" + "\n")
            log.write("\t\t Image number: " + str(images_requested + 1) + "\n")

            if image_name is not None:
                log.write("\t\t Image name: " + str(image_name) + "\n")
            else:
                log.write("\t\t Image name: Error getting name\n")
            if image_ext is not None:
                log.write("\t\t Image ext: " + str(image_ext) + "\n")
            else:
                log.write("\t\t Image name: Error getting ext\n")
            log.write("\t\t Image requested from " + str(image_links[images_requested]) + "\n")

            print("\t Image info: [IO ERROR]")
            print("\t\t Image number: " + str(images_requested + 1))

            if image_name is not None:
                print("\t\t Image name: " + str(image_name))
            else:
                print("\t\t Image name: Error getting name")
            if image_ext is not None:
                print("\t\t Image ext: " + str(image_ext))
            else:
                print("\t\t Image ext: Error getting ext")
            print("\t\t Image requested from " + str(image_links[images_requested]))

            images_requested += 1
            continue

        except TimeoutError:
            log.write("\t Image info: [TIMEOUT ERROR]" + "\n")
            log.write("\t\t Image number: " + str(images_requested + 1) + "\n")

            if image_name is not None:
                log.write("\t\t Image name: " + str(image_name) + "\n")
            else:
                log.write("\t\t Image name: Error getting name\n")
            if image_ext is not None:
                log.write("\t\t Image ext: " + str(image_ext) + "\n")
            else:
                log.write("\t\t Image name: Error getting ext\n")

            log.write("\t\t Image requested from " + str(image_links[images_requested]) + "\n")

            print("\t Image info: [TIMEOUT ERROR]")
            print("\t\t Image number: " + str(images_requested + 1))

            if image_name is not None:
                print("\t\t Image name: " + str(image_name))
            else:
                print("\t\t Image name: Error getting name")
            if image_ext is not None:
                print("\t\t Image ext: " + str(image_ext))
            else:
                print("\t\t Image ext: Error getting ext")

            print("\t\t Image requested from " + str(image_links[images_requested]))

            images_requested += 1
            continue

        except IndexError:
            log.write("\t Image info: [INDEX ERROR]" + "\n")
            log.write("\t\t Image number: " + str(images_requested + 1) + "\n")

            if image_name is not None:
                log.write("\t\t Image name: " + str(image_name) + "\n")
            else:
                log.write("\t\t Image name: Error getting name\n")
            if image_ext is not None:
                log.write("\t\t Image ext: " + str(image_ext) + "\n")
            else:
                log.write("\t\t Image name: Error getting ext\n")

            log.write("\t\t Image requested from " + str(image_links[images_requested]) + "\n")
            images_requested += 1

            print("\t Image info: [INDEX ERROR]")
            print("\t\t Image number: " + str(images_requested + 1))
            if image_name is not None:
                print("\t\t Image name: " + str(image_name))
            else:
                print("\t\t Image name: Error getting name")
            if image_ext is not None:
                print("\t\t Image ext: " + str(image_ext))
            else:
                print("\t\t Image ext: Error getting ext")
            print("\t\t Image requested from " + str(image_links[images_requested]))

            continue

        except Exception:
            log.write("\t Image info: [GENERIC ERROR]" + "\n")
            log.write("\t\t Image number: " + str(images_requested + 1) + "\n")

            if image_name is not None:
                log.write("\t\t Image name: " + str(image_name) + "\n")
            else:
                log.write("\t\t Image name: Error getting name\n")
            if image_ext is not None:
                log.write("\t\t Image ext: " + str(image_ext) + "\n")
            else:
                log.write("\t\t Image name: Error getting ext\n")

            log.write("\t\t Image requested from " + str(image_links[images_requested]) + "\n")
            images_requested += 1

            print("\t Image info: [INDEX ERROR]")
            print("\t\t Image number: " + str(images_requested + 1))
            if image_name is not None:
                print("\t\t Image name: " + str(image_name))
            else:
                print("\t\t Image name: Error getting name")
            if image_ext is not None:
                print("\t\t Image ext: " + str(image_ext))
            else:
                print("\t\t Image ext: Error getting ext")
            print("\t\t Image requested from " + str(image_links[images_requested]))

            continue

        images_requested += 1

    log.close()

if __name__ == "__main__":

    all_user_search_queries = []  # The list of all the queries given by the user/file

    # Loads queries from a txt file if provided, each query is separated by a \n character
    if os.path._getfullpathname(str("words.txt")):

        search_file = open(str(os.path._getfullpathname("words.txt")), 'r')

        print("Loading queries from file\n")

        for word in search_file:
            all_user_search_queries.append(str(word))

        print("Done loading queries from file\n")

    else:
        # Gets all the queries from the user
        while True:
            query = input("Enter in the queries you want to download. Press enter to move to the next query and "
                          "'go' to start downloading \n")

            if str(query).lower() == "go":
                break
            else:
                all_user_search_queries.append(str(query))

    # Gets the amount of images to download for all queries
    while True:
        try:
            amount_download = input("Enter in the amount of images you would like to download between 1 and 100\n")

        except ValueError:
            print("Enter in a valid number between 1 and 100\n")

        if str(amount_download).isnumeric() and (int(amount_download) in range(1 , 1000)):
            break

    amount_download = int(amount_download)  # The amount of images to download (1 < amount <= 100)

    '''
    The regex used to identify a valid folder name
        Matches all of the following characters (this expression is reversed when finding valid folder names)
            OR, *, -, ", /, \, :, ?, |, ., site:, related:, #, @, $, %
    '''
    folder_name_regex = re.compile(r"-\w*|OR|\*|\"|-|/|\\|:|\$|%|\?|\||\w*\.\w*|site:|related:|#\w*|@\w*",
                                   re.MULTILINE)

    folder_names = []  # The names of all the folders created for all the queries

    ''' Removes all special terms from google current_query query and then removes all the additional whitespace
        between character '''
    for i in range(len(all_user_search_queries)):
        ''' Replaces all the special terms with '', removes all of Google special search modifier syntax
            Google Search Syntax: https://support.google.com/websearch/answer/2466433?hl=en'''
        individual_search_terms = re.sub(folder_name_regex, '', all_user_search_queries[i]).strip(' ')

        # Fins all the words from the current query and makes those set of words the folder name
        folder_names.append(' '.join(re.findall(r"\w+", individual_search_terms, re.MULTILINE)))

    try:
        '''Creates a subdirectory to store all of the downloaded images folders, then switches to that folder to make
           it the new working directory for the paths'''
        if not os.path.isdir("Downloaded_Images"):
            os.mkdir("Downloaded_Images")
            os.chdir("Downloaded_Images")
        else:
            os.chdir("Downloaded_Images")
    except IOError:
        print("There was an error creating the 'Download_Images' save location, program is now exiting")
        exit(1)

    current_query_number = 0  # The current query being worked on from the all_user_search_queries list

    # Loops through the all_user_search_queries list and downloads their respective images
    while current_query_number < len(all_user_search_queries):

        query_all_image_links = []  # Links of all the images in the page

        # Checks to see if the folder of the images already exists, creates a folder for each query
        if not os.path.isdir(folder_names[current_query_number]):
            try:

                ''' Makes sure folder name length conforms to less that 60 characters, otherwise OS's have
                    problems with them '''
                if len(folder_names[current_query_number]) > 60:
                    # Grabs 250 characters from the initial name
                    revised_file_name = folder_names[current_query_number][0:60]
                    os.makedir(revised_file_name)
                else:
                    os.makedirs(folder_names[current_query_number])
            except IOError:
                print("There was a problem creating the directory, moving onto next query")
                continue
            except IndexError:
                print("There was a problem with the directory file name, moving onto next query")
                continue

        # The location where each query's respective images will be saved
        images_save_location_path = str(os.path._getfullpathname(folder_names[current_query_number]))

        grab_query_links_time_start = time.time()  # The start time of how long it took to grab all query image links

        print("Evaluating query: " + folder_names[current_query_number])

        ''' %20, the 20 is ASCII for a space character, the % allows it to be used within the URL which
            would not be usually allowed '''
        current_query = all_user_search_queries[current_query_number].replace(' ', '%20')

        limit_to_week = "&as_qdr=w"  # Limits the current_query results to ones from past week only
        safe_search = "&safe=active"  # Turns on Google's safe current_query feature to filter out explicit content
        # The google images page of the requested query, the '&tbm=isch' explicitly loads the query's result page
        url = 'https://www.google.com/search?q=' + current_query + '&tbm=isch'
        raw_html = (_download_page_html(url))

        # Gets all the links of images on the google image's page
        query_all_image_links += _get_all_links_from_page(raw_html)

        # If google does not have any images for the query
        if query_all_image_links[0][0:4] == "type":
            print("Google could not process your query, moving to next query")
            current_query_number += 1
            continue

        grab_query_links_time_end = time.time()  # The end time of how long it took to grab all query image links
        total_grab_query_links_time = grab_query_links_time_end - grab_query_links_time_start
        print("Total time taken: " + str(total_grab_query_links_time) + " seconds")

        print("Starting download for query: " + folder_names[current_query_number])

        # Downloads all images from their respective links
        _download_all_images(folder_names[current_query_number], query_all_image_links)

        current_query_number += 1

    if len(query_all_image_links) == 0:
        print("All queries were skipped because google could not process them")
    else:
        print("\nFinished downloading all images")
