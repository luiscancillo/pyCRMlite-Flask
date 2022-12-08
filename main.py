''' main.py
This script is just an example of a back-end web application to explode a relational database containing data on
customer and products (a kind of oversimplified Customer Relationship Management (CRM).
It has been implemented to evaluate the use of Flask to support web page interaction whit regard to other alternatives.
The solution implemented uses a structured approach, where a set of functions are defined to perform the functionalities
requested.
'''

from flask import render_template, Flask, request
import sqlite3
import matplotlib

matplotlib.use('Agg')   # see 'Matplotlib in a web application server' for understanding this issue
import matplotlib.pyplot as plt

# Set the application as a Flask object
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    '''
    index sends to the browser the index page.
    With the app.route decorator stated, this function it is called by Flask when the URL root is set in the browser.
    For example: http://localhost/
    :return: the initial web page
    '''
    return render_template('index.html')

@app.route('/identify', methods=['POST', 'GET'])
def identify():
    '''
    identify gets form data from 'index' page when the 'identify' request in it is sent by the browser. This request
    includes the user identification input in the form and triggers the action to send to the browser a new page
     depending on the type of user selected.
    :return: the web page with user related data, or the error message in case of erroneous input data
    '''
    #get the user identification input in the browser and extract from the database the data related
    if request.method == 'POST':
        userId = request.form['userId']
    else:
        userId = request.args.get('userId')
    if userId.strip() == "":
        error = "Please, introduce a user identification"
        return render_template('index.html', error=error)
    userRegister, userList = getUserData(userId)
    if userRegister['admin'] == 'checked':
        return makeAdminPage()
    elif userRegister['supplier'] == 'checked':
        return makeSupplierPage(userRegister)
    elif userRegister['customer'] == 'checked':
        return makeCustomerPage(userRegister)
    error = "This user identification doesn't exist"
    return render_template('index.html', error=error)

@app.route('/updateusers', methods=['POST', 'GET'])
def updateusers():
    '''
    updateusers sends to the browser the page 'updateusers' filled with the list of users extracted from the database,
    an empty user register, and undefined user type.
    The 'updateusers' page contains a drop-down to be filled with the existing users in the database, to allow selection
    of the one to be processed.
    :return: the updateuser page rendered with the user list
    '''
    userRegister, userList = getUserData()
    return render_template('updateusers.html',
                           users=userList,
                           selected_user=userRegister,
                           error="")

@app.route('/displayuser', methods=['POST', 'GET'])
def displayuser():
    '''
    displayuser sends to the browser the updateusers page filled with data related to the selected user, filling every
    field with the corresponding data extracted from the database.
    :return: the updateusers page rendered with its register data
    '''
    if request.method == 'POST':
        userId = request.form['userId']
    else:
        userId = request.args.get('userId')
    userRegister, userList = getUserData(userId)
    return render_template('updateusers.html',
                           users=userList,
                           selected_user=userRegister,
                           error="")

@app.route('/saveuser', methods=['POST'])
def saveuser():
    '''
    saveuser performs one of the following main tasks, depending on the user request:
    1) update; update the record of the selected user saving the current data in the database. The user id cannot be
     changed and shall exist in the database. If for any reason (i.e. concurrent access to the database) it does not
    exist, an advisory error message and the form data is sent to the browser alerting on this unaffordable update.
    2) new; adds a new user to the database. If the user identification already exist in the database, an advisory
    error message and the form data is sent to the browser alerting on this unaffordable add.
    3)delete; it deletes from the database the current user register. If the user identification of the register to be
    deleted doesn't exist, an advisory error message and the form data is sent to the browser alerting on this
    unaffordable delete.
    :return: a html page rendered according the result from the above tasks
    '''
    # sets an empty register and gets the user list from the database
    userRegister, userList = getUserData()
    #fills the user register dictionary with all the values from the page
    for k in request.form.keys():
        userRegister[k] = request.form[k]
    error = ""
    try:
        dbConexion = sqlite3.connect('data.db')
        cursor = dbConexion.cursor()
        if "update" in request.form.keys():
            # sets the SQL query to update the current register
            query = 'UPDATE users SET name=:name,street=:street,city=:city,' \
                   'state=:state,iban=:iban,payment=:payment,etc=:etc,customer=:customer,' \
                   'supplier=:supplier,admin=:admin,password=:password WHERE id=:id'
            cursor.execute(query, userRegister)
            error = "The number of updated registers is " + str(cursor.rowcount)
            if cursor.rowcount == 0:
                # error occurred: create the related error message and returns the page with the current contents
                error += " : The id you have select doesn't exist"
                return render_template('updateusers.html',
                           users=userList,
                           selected_user=userRegister,
                           error=error)
            dbConexion.commit()
        elif "new" in request.form.keys():
            if len(userRegister["id"].strip()) != 0:
                # only non empty user id are allowed. Sets the SQL query to add the register to the database
                query = 'INSERT INTO users VALUES(:id,:name,:street,:city,:state,:iban,:payment,:etc,:customer,'\
                        ':supplier,:admin,:password)'
                try:
                    cursor.execute(query, userRegister)
                    error = "The number of inserted registers is " + str(cursor.rowcount)
                    dbConexion.commit()
                except:
                    # catch most likely error of duplicated user identification: returns the page with current contents
                    error += " The user id shall be unique."
                    return render_template('updateusers.html',
                                            users=userList,
                                            selected_user=userRegister,
                                            error=error)
            else:
                error = "The user id cannot be empty "
                return render_template('updateusers.html',
                                       users=userList,
                                       selected_user=userRegister,
                                       error=error)
        elif "delete" in request.form.keys():
            # delete the current user register
            if userRegister["id"] in userList:
                query = 'DELETE FROM users WHERE id = ?'
                cursor.execute(query,(userRegister["id"],))
                error = "Deleted rows:" + str(cursor.rowcount)
                dbConexion.commit()
            else:
                # set an error, in case of non-existence of id's element that we want to delete
                error = "The id you put in doesn't exist"
                return render_template('updateusers.html',
                                       users=userList,
                                       selected_user=userRegister,
                                       error=error)
    except sqlite3.Error as sqlerror:
        error = sqlerror
    dbConexion.close()
    userRegister, userList = getUserData()
    return render_template('updateusers.html',
                           users=userList,
                           selected_user=userRegister,
                           error=error)

@app.route('/updateproducts', methods=['POST', 'GET'])
def updateproducts():
    '''
    updateproducts sends to the browser the page 'updateproducts' filled with the list of users extracted from the
    database, an empty user register, and undefined user type.
    The 'updateproducts' page contains a drop-down to be filled with the existing products in the database, to allow
    selection of the one to be processed.
    :return: the updateproducts page rendered with the user list
    '''
    productRegister, productList = getProductData()
    return render_template('updateproducts.html',
                           products=productList,
                           selected_product=productRegister,
                           error="")

@app.route('/displayproduct', methods=['POST', 'GET'])
def displayproduct():
    '''
    displayproduct sends to the browser the update products page with data related to the selected product, filling
    every field with the corresponding data extracted from the database.
    :return: the updateproducts page rendered with its register data
    '''
    if request.method == 'POST':
        productId = request.form['productId']
    else:
        productId = request.args.get('productId')
    productRegister, productList = getProductData(productId)
    return render_template('updateproducts.html',
                           products=productList,
                           selected_product=productRegister,
                           error="")

@app.route('/saveproduct', methods=['POST'])
def saveproduct():
    '''
    saveproduct performs one of the following main tasks, depending on the user request:
    1) update; update the record of the selected product saving the current data in the database. The product id cannot
    be changed and shall exist in the database. If for any reason (i.e. concurrent access to the database) it does not
    exist, an advisory error message and the form data is sent to the browser alerting on this unaffordable update.
    2) new; adds a new product to the database. If the product identification already exist in the database, an advisory
    error message and the form data is sent to the browser alerting on this unaffordable add.
    3)delete; it deletes from the database the current product register. If the product identification of the register
    to be deleted doesn't exist, an advisory error message and the form data is sent to the browser alerting on this
    unaffordable delete.
    :return: a html page rendered according the result from the above tasks
    '''
    # sets an empty register and gets the product list from the database
    productRegister, productList = getProductData()
    #fills the product register dictionary with all the values from the page
    for k in request.form.keys():
        productRegister[k] = request.form[k]
    error = ""
    try:
        dbConexion = sqlite3.connect('data.db')
        cursor = dbConexion.cursor()
        if "update" in request.form.keys():
            # sets the SQL query to update the current register
            query= 'UPDATE products SET name=:name,location=:location,price=:price,minimunstock=:minimunstock,' \
                   'initialstock=:initialstock,tax=:tax,description=:description WHERE id=:id'
            cursor.execute(query, productRegister)
            error = "The number of updated registers is " + str(cursor.rowcount)
            #create an error wich appears in the page, in case of inexistence of the selected id
            if cursor.rowcount == 0:
                # error occurred: create the related error message and returns the page with the current contents
                error += " : The product id you have select doesn't exist"
                return render_template('updateproducts.html',
                           products=productList,
                           selected_products=productRegister,
                           error=error)
            dbConexion.commit()
        elif "new" in request.form.keys():
            # add to the database with a new product
            if len(productRegister["id"].strip()) != 0 :
                # only non-empty product id are allowed. Sets the SQL query to add the register to the database
                query = 'INSERT INTO products VALUES(:id,:name,:location,:price,:minimunstock,:initialstock,:tax,' \
                        ':description)'
                try:
                    cursor.execute(query, productRegister)
                    error = "The number of inserted registers is " + str(cursor.rowcount)
                    dbConexion.commit()
                except:
                    # catch most likely error of duplicated product id: returns the page with current contents
                    error += " The product id shall be unique."
                    return render_template('updateproducts.html',
                                            products=productList,
                                            selected_product=productRegister,
                                            error=error)
            else:
                error = "The product id cannot be empty "
                return render_template('updateproducts.html',
                                       products=productList,
                                       selected_product=productRegister,
                                       error=error)
        elif "delete" in request.form.keys():
            if productRegister["id"] in productList:
                query = 'DELETE FROM products WHERE id = ?'
                cursor.execute(query, (productRegister["id"],))
                error = "Deleted rows:" + str(cursor.rowcount)
                dbConexion.commit()
            else:
                # set an error, in case of non-existence of id's element that we want to delete
                error = "The id you put in doesn't exist"
                return render_template('updateproducts.html',
                                       products=productList,
                                       selected_product=productRegister,
                                       error=error)
    except sqlite3.Error as sqlerror:
        error=sqlerror
    dbConexion.close()
    productRegister,productList = getProductData()
    return render_template('updateproducts.html',
                           products=productList,
                           selected_product=productRegister,
                           error=error)

@app.route('/updateactivity', methods=['POST', 'GET'])
def updateactivity():
    '''
    updateactivity sends to the browser the page 'updateactivity' filled with the list of activities extracted from the
    database, an empty activity register, the product list, and the user list.
    The 'updateactivity' page contains drop-downs for:
    1) the activities existing in the database (only date and product id are shown)
    2) the product identifiers
    3) the user identifiers
    :return: the updateactivity page rendered with the activity list
    '''
    userRegister, userList = getUserData()
    productRegister, productList = getProductData()
    activityRegister, activityList = getactivityData()
    return render_template('updateactivity.html',
                           activity=activityList,
                           selected_activity=activityRegister,
                           products=productList,
                           users=userList,
                           error="")

@app.route('/displayactivity', methods=['POST', 'GET'])
def displayactivity():
    '''
    displayactivity sends to the browser the updateactivity page filled with data related to the selected user, filling
    every field with the corresponding data extracted from the database.
    :return: the updateactivity page rendered with above data
    '''
    if request.method == 'POST':
        activityId = request.form['activityId']
    else:
        activityId = request.args.get('activityId')

    userRegister, userList = getUserData(activityId)
    productRegister, productList = getProductData(activityId)
    activityRegister, activityList = getactivityData(activityId)
    return render_template('updateactivity.html',
                           activity=activityList,
                           selected_activity=activityRegister,
                           products=productList,
                           users=userList,
                           error="")

@app.route('/saveactivity', methods=['POST'])
def saveactivity():
    '''
    saveactivity performs one of the following main tasks, depending on the user request:
    1) update; update the record of the selected activity saving the current data in the database. The activity id
     cannot be changed and shall exist in the database. If for any reason (i.e. concurrent access to the database)
     it does not exist, an advisory error message and the form data is sent to the browser alerting on this unaffordable
    update.
    2) new; adds a new activity to the database.
    3)delete; it deletes from the database the current user register. If the user identification of the register to be
    deleted doesn't exist, an advisory error message and the form data is sent to the browser alerting on this
    unaffordable delete.
    :return: a html page rendered according the result from the above tasks
    '''
    # sets an empty register and gets the lists from the database
    userRegister, userList = getUserData()
    productRegister, productList = getProductData()
    activityRegister, activityList = getactivityData()
    #fills the activity register dictionary with all the values from the page
    for k in request.form.keys():
        activityRegister[k] = request.form[k]
    error = ""
    try:
        dbConexion = sqlite3.connect('data.db')
        cursor = dbConexion.cursor()
        if "update" in request.form.keys():
            # sets the SQL query to update the current register
            query = 'UPDATE activity SET idproduct=:idproduct,inout=:inout,idsuppocust=:idsuppocust,' \
                   'price=:price,date=:date,serialnum=:serialnum, etc=:etc WHERE id=:id'
            cursor.execute(query, activityRegister)
            error = "The number of updated registers is " + str(cursor.rowcount)
            if cursor.rowcount == 0:
                # create an error which appears in the page, in case of non-existence of the selected id
                error += " : The id you have select doesn't exist"
                return render_template('updateactivity.html',
                           activity=activityList,
                           selected_activity=activityRegister,
                           products=productList,
                           users=userList,
                           error=error)
            dbConexion.commit()
        elif "new" in request.form.keys():
            query = 'INSERT INTO activity (idproduct,inout,idsuppocust,price,date,serialnum,etc)' \
                   'VALUES(:idproduct,:inout,:idsuppocust,:price,:date,:serialnum,:etc)'
            cursor.execute(query, activityRegister)
            error = "The number of inserted registers is " + str(cursor.rowcount)
            dbConexion.commit()
        elif "delete" in request.form.keys():
            for a in activityList:
                if int(activityRegister["id"]) == a[0]:
                    query = 'DELETE FROM activity WHERE id = ?'
                    cursor.execute(query,(activityRegister["id"],))
                    error = "Deleted rows:" + str(cursor.rowcount)
                    dbConexion.commit()
                    break
            else:
                error += " The id you put in doesn't exist"
                return render_template('updateactivity.html',
                                       activity=activityList,
                                       selected_activity=activityRegister,
                                       products=productList,
                                       users=userList,
                                       error=error)
        dbConexion.close()
    except sqlite3.Error as sqlerror:
        error = sqlerror
    # sets an empty register and gets activity list from the database
    activityRegister, activityList = getactivityData()
    return render_template('updateactivity.html',
                           activity=activityList,
                           selected_activity=activityRegister,
                           products=productList,
                           users=userList,
                           error=error)

def hbarsPlot (pltData, pltTitle, pltXlabel, pltYlable, fileName):
    '''
    hbarsPlot plots a simple horizontal bar chart with data passed
    :param pltData: a dictionary with keys (in y) and values (in x)
    :param pltTitle: title of the figure
    :param pltXlabel: the label for y
    :param pltYlable: the lable for x
    :param fileName: the name of the file to save the figure
    :return:
    '''
    plt.clf()
    plt.title(pltTitle)
    plt.xlabel(pltXlabel)
    plt.ylabel(pltYlable)
    plt.barh(list(pltData.keys()), list(pltData.values()))
    plt.savefig('static/img/' + fileName)

def getPeriod():
    '''
    Gets the initial and final date of the period activities in the BD
    :return: initial and final date
    '''
    dbConexion = sqlite3.connect('data.db')
    cursor = dbConexion.cursor()
    cursor.execute('SELECT MIN(date) FROM activity')
    initial = cursor.fetchone()
    cursor.execute('SELECT MAX(date) FROM activity')
    final = cursor.fetchone()
    dbConexion.close()
    return initial[0], final[0]

def queryActivity(user, inout):
    '''
    Performs the query on the DB extracting all products having activity (purchase or sale) in the period, and it cost
    or price.
    :param user: the user identification
    :param inout: the activity movements to be computed: "C" (inputs or purchase), "V" (outputs or sale)
    :return: a list of registers, each one containing the product name and cost or price
    '''
    dbConexion = sqlite3.connect('data.db')
    cursor = dbConexion.cursor()
    query = 'SELECT products.name, activity.price FROM products, activity WHERE activity.idproduct = products.id'
    if len(inout) != 0:
        query += ' AND activity.inout = "' + inout + '"'
    if len(user) != 0:
        query = query + ' AND activity.idsuppocust = "' + user + '"'
    cursor.execute(query)
    allActs = cursor.fetchall()
    dbConexion.close()
    return allActs

def makeAdminPage():
    '''
    makeAdminPage collect data related to all sales and purchases registered in the BD, and builds the web page
    to show this data.
    :return: the web page with administrator related data
    '''
    # put in a dictionary the sales per product during current period and plot them
    dicData = getValues('V')
    hbarsPlot(dicData, 'Sales per product', 'Sales', 'Product', 'graph-admin-sales.jpg')
    # compute the total amount of sales
    totalSales = 0
    for product, price in dicData.items():
        totalSales += price
    # put in a dictionary the accumulated outputs for each product and generate the graph
    dicData = getActivity('', 'V')
    hbarsPlot(dicData, 'Units sold', 'Units', 'Product', 'graph-admin-units-sold.jpg')
    # put in a dictionary the accumulated inputs for each product and compute balance
    balance = getActivity('', 'C')
    # compute the net balance of inventory
    for product, cant in dicData.items():
        if product in balance:
            balance[product] = balance[product] - cant
        else:
            balance[product] = -cant
    # plot balance
    hbarsPlot(balance, 'Product balance', 'Outputs minus inputs', 'Product', 'graph-admin-inventory.jpg')
    initialDate, finalDate = getPeriod()
    return render_template('admin.html',
                           initial=initialDate,
                           final=finalDate,
                           sales=totalSales,
                           alerts=stockAlert(balance))

def makeSupplierPage(regCoP):
    '''
    makeSupplierPage collects data on all supplies from the BD for a given supplier and builds a web page to show them.
    :param regCoP: a register with the supplier identification data
    :return: the web page with supplier related data
    '''
    # the register to keep data of the client or supplier
    # put in a dictionary the supplies per product during period and plot them
    supplies = getActivity(regCoP.get("id"), 'C')
    hbarsPlot(supplies, 'Supplies per product', 'Supply', 'Product', 'graph-supplier.jpg')
    initialDate, finalDate = getPeriod()
    return render_template('supplier.html',
                           supplier=regCoP,
                           initial=initialDate,
                           final=finalDate)

def makeCustomerPage(regCoP):
    '''
    makeCustomerPage collects data on all sales from the BD to a given customer and builds a web page to show them.
    :param regCoP: a register with the customer identification data
    :return: the web page with customer related data
    '''
    # put in a dictionary the sales per product during period and plot them
    sales = getActivity(regCoP.get("id"), 'V')
    hbarsPlot(sales, 'Sales per product', 'Sales', 'Product', 'graph-customer.jpg')
    initialDate, finalDate = getPeriod()
    return render_template('customer.html',
                           customer=regCoP,
                           initial=initialDate,
                           final=finalDate)

def stockAlert(balance):
    '''
    stckAlert computes the current amount of existences for each product and determines if its level is below the
    minimum requested. In this case, an alert flag is raised for the product.
    :param balance: a dictionary with the net amount of inputs minus outputs for each product during the current period
    :return: the list of products below the alert level
    '''
    dbConexion = sqlite3.connect('data.db')
    cursor = dbConexion.cursor()
    query = 'SELECT name, initialstock, minimunstock, location FROM products'
    cursor.execute(query)
    regProd= cursor.fetchall()
    dbConexion.close()
    # update balance of the period with the initial stock
    for reg in regProd:
        product = reg[0]
        if product in balance:
            balance[product] = balance[product] + reg[1]
        else:
            balance[product] = reg[1]
    # make a list with the products being below the minimum stock
    productsBelowLevel = []
    for reg in regProd:
        name = reg[0]
        min = reg[2]
        if name in balance:
            stock = balance[name]
            if stock < min:
                productsBelowLevel.append([name, reg[3], min, stock])
    return productsBelowLevel

def getUserData(identification=""):
    '''
    getUserData checks if the given user identification is correct, and returns the type of user it is and its register.
    :param identification: the user identification
    :return: the user register (a dictionary), and the list of user identifications
    '''
    dbConexion = sqlite3.connect('data.db')
    cursor = dbConexion.cursor()
    # generate the user identification list extracting from the tuples got from the query the id (1st element)
    cursor.execute('SELECT id FROM users')
    userList = [u[0] for u in cursor.fetchall()]
    # and insert a blank in the first place: the list is shown in a drop-down, and the 1st place should be blank
    userList.insert(0, " ")
    # extract the user register and other useful data
    cursor.execute('SELECT * FROM users WHERE id = "' + identification + '"')
    # extract the list of columns in the user table
    userCols = [col[0] for col in cursor.description]
    userData = cursor.fetchone()
    if userData != None:
        # fill a dictionary with the column name as key and the related user data as value
        userDict = dict((userCols[i], userData[i]) for i in range(len(userCols)))
    else:
        # fill a dictionary with the column name as key and an empty value
        userDict = dict((userCols[i], "") for i in range(len(userCols)))
    dbConexion.close()
    return userDict, userList

def getActivity(user, inout):
    '''
    getActivity computes the number of inputs or outputs for the existing products for a given user.
    :param user: the user identification
    :param inout: the activity movements to be computed: "C" (input/purchase), "V" (output/sale)
    :return: a dictionary with product id as key and total amount of units as value
    '''
    # get the requested inputs and/or outputs for the given user (if any)
    allActs = queryActivity(user, inout)
    # put in a dictionary product id as key and total amount of units as value
    actProduct = {}
    for reg in allActs:
        # get product name and update counters in the dictionary
        product = reg[0]
        if product in actProduct:
            actProduct[product] = actProduct[product] + 1
        else:
            actProduct[product] = 1
    return actProduct

def getValues(inout):
    '''
    getValues computes the value of sales or purchases of each product for the period
    :param inout: the movements to be computed: "C" (inputs/purchases), "V" (outputs/sales)
    :return: a dictionary with accumulated price values of each product for the period
    '''
    # get the requested inputs or outputs
    allActs = queryActivity('', inout)
    # a dictionary to accumulate amounts: key is the product id and value the accumulated amount
    actProduct = {}
    for reg in allActs:
        # product name is in col 0 and price in col 1
        product = reg[0]
        if product in actProduct:
            actProduct[product] = actProduct[product] + reg[1]
        else:
            actProduct[product] = reg[1]
    return actProduct

def getProductData(identification=""):
    '''
    getUserData checks if the given identification for a product is correct, and returns the product register and the
    list of existing products.
    :param identification: the product identification
    :return: the product register as a dictionary and the list of products id
    '''
    # see getUserData comments. This function has the same logic
    dbConexion = sqlite3.connect('data.db')
    cursor = dbConexion.cursor()
    cursor.execute('SELECT id FROM products')
    productList = [p[0] for p in cursor.fetchall()]
    productList.insert(0, " ")
    cursor.execute('SELECT * FROM products WHERE id = "' + identification + '"')
    productCols = [col[0] for col in cursor.description]
    productData = cursor.fetchone()
    if productData != None:
        productDict = dict((productCols[i], productData[i]) for i in range(len(productCols)))
    else:
        productDict = dict((productCols[i], "") for i in range(len(productCols)))
    dbConexion.close()
    return productDict, productList

def getactivityData(identification=""):
    '''
    getUserData checks if the given activity identification is correct, and returns the activity register and the list
    of existing activities.
    :param identification: the activity identification
    :return: the activity register as a dictionary and the list of activities in the DB
    '''
    # see getUserData comments. This function has the same logic
    dbConexion = sqlite3.connect('data.db')
    cursor = dbConexion.cursor()
    cursor.execute('SELECT id,idproduct,date FROM activity')
    activityList = cursor.fetchall()
    activityList.insert(0,(" ","",""))
    cursor.execute('SELECT * FROM activity WHERE id = "' + identification + '"')
    activityCols = [col[0] for col in cursor.description]
    activityData = cursor.fetchone()
    if activityData != None:
        activityDict = dict((activityCols[i], activityData[i]) for i in range(len(activityCols)))
    else:
        activityDict = dict((activityCols[i], "") for i in range(len(activityCols)))
    dbConexion.close()
    return activityDict, activityList

if __name__ == "__main__":
    # run the Flask application 'in code'
    # shall be only here to avoid problems when deployed using Apache
    app.run(host="0.0.0.0", debug=True)
