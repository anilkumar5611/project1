from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

application = Flask(__name__)


# base url + /
#http://127.0.0.1:8001 + /
@application.route('/',methods=['GET'])  # route to display the home page
@cross_origin()         # Used for deploying it over the cloud platform
def homePage():
    return render_template("index.html")

@application.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")          ## obtaining the search string entered in the form
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString        # preparing the URL to search the product on flipkart
            uClient = uReq(flipkart_url)         ## requesting the webpage from the internet
            flipkartPage = uClient.read()        # reading the webpage
            uClient.close()          # closing the connection to the web server
            flipkart_html = bs(flipkartPage, "html.parser")         # parsing the webpage as HTML(structered data with tag)
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})         # seacrhing for appropriate tag to redirect to the product link
            del bigboxes[0:3]               # the first 3 members of the list do not contain relevant information, hence deleting them.
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']    # extracting the actual product link
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")    # Parsing the product page as HTML
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})


            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)


            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                # try:    
                #     fw = open(filename, "a")
                #     fw.writelines([searchString,name,rating,commentHead,custComment])
                #     #fw.write(f"{searchString},{name},{rating},{commentHead},{custComment}")
                # except Exception as e:
                #     print('The Exception message is: ',e)
                #     return 'Error in saving the details of the product'


                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    application.run(host='0.0.0.0')    
    #app.run(host='0.0.0.0', port=8001, debug=True) #For local system and lab
	#app.run(debug=True)
