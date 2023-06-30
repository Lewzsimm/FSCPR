# FSCPR
Food Service Check Prepare Rotate - Python3 SQL Flask Application

#FSCPR - Food Service: Check, Prepare, Rotate
#### Video Demo: [https://youtu.be/CBqh6Csj6eI](https://youtu.be/CBqh6Csj6eI) <url>
(Created as my final project for Harvard's CS50X)


##Usage:
FSCPR is a food production inventory assistant application that lets you know what is in your storage, when it was made, when it expires and what needs to be prepared; accessable from anywhere, at any time.
From using the "FIFO" section to prioritize specials, to the "Prep" section for creating prep lists, or just letting Chefs see what is in stock; FSCPR aims to conviently deliver stock information on demand.   

##Getting started:

Admin must first log in, as only an administrator may register new users.
The Admin account will come preset, and the Admin's home screen will have a unique "Admin" option.
The Admin account will have and id of 1, Username = "Admin", and password = "fscpr". 
This should not be changed or deleted from within the sql database, nor within "main.html" without ensuring congruency between the two.

Once logged in to the admin account, the user will be greeted with the main menu, and should navigate to the "Admin" tab.
From within the admin tab, navigate to the "+ User" tab.
Here, the admin may register new user accounts. 

After registering a new user, that account may be granted admin authority if desired, this can be done by:
1. Opening the SQL database, and retreiving the account's id.
2. "main.html" must then be opened using an editor
3. Navigate to line 46, and add the following:
> `or (session["user_id"] == x)` 
,where x = the id of the user we wish to grant admin menu access.
IE:
>    Before: `{% if (session["user_id"] == 1) %}`
>    After: `{% if (session["user_id"] == 1) or (session["user_id"] == x) %}`
Multiple users may be granted admin access by repeating this step for each respective user.
>This information can't be seen by unregistered users, as accessing the page requires a valid account, otherwise the user is served index.html, and will not be served main.html.

##Admin Menu:
The admin menu contains 5 options:
1. "+ Cooler"
2. "+ Freezer"
3. "+ Dry"
4. "+ User"
5. "- User"

All inventory areas should be initialized using their associated options.
Once a new storage unit is added, the user will be redirected to the menu page of it's respective category.
If for example, our kitchen had one walk-in cooler, and two line fridges that we would like to add, we would have to navigate to + Cooler for each, adding and naming each unit, after which these will now appear in the "Cooler" category from within the main menu.
> Note that deleting all lines from within any perspective storage unit will result in the unit becoming removed from it's parent menu, effectively deleting it, and so will have to be re-added using the above method if it is to be included again. 
>To avoid this, it is recommended to leave one item in what may otherwise be an empty storage unit to avoid necessitating it's re-creation. 
>This choice was made as it gives users a way to delete temporary storage units without having Admin access. Most often, any regular storage unit will never have "nothing" in it's inventory, making the accidental deletion of dedicated storage areas which then require Admin access to re-create, unlikely.

Newly created storage areas will be initialized with a placeholder entry. This may be deleted after adding new inventory for the first time to the unit.

The "-User" option will display a table containing all registered users, which may be selected for deletion, excluding the "Admin" account.
This is a perminant deletion, but will not erase any records of said user's updates until effected items are again updated by another user(see below).

##"Hamburger-Menu" Navigation
Areas that do not have dedicated back/forward buttons will display a "Hamburger-icon" which when clicked, will reveal a drop-down navigation menu.
While viewing storage contents, the "Update" button can be found within the Hamburger-Menu.

##Main Menu
contents:
1. Cooler
2. Freezer
3. Dry
4. Prep
5. FIFO
6. Logout

Cooler/Freezer/Dry:
These options lead to a menu containing any storage areas that have been added to their respective categories.

Prep:
Displays a table of all items, throughout all storage areas, that have their "prep flag" set to "on" (more below)

FIFO:
Displays a table of all items, throughout all storage areas, that are nearing(within 3 days) or have passed their expiry date.

Logout:
This option clears any session data, logs the user out, and returns them to the login screen.

##Accessing Storage:

Selecting Dry, Cooler, or Freezer from the main menu will bring the user to a menu screen containing any added storage areas, which can then be selected and opened.
Once a storage unit has been opened, the user will be met with a table displaying the contents of the storage unit, first ordered by Shelf, and second by name.
Each item contains the following:
1. Name

The Name of the item

2. Brand

The brand of the item(optional)

3. Production

The date the item was made

4. Expiry

The date the item expires, or is best before

5. #Ptns

The number of individual prepared portions of this item

6. #Batches

The number of full batches of this item

7. #Ptns/Batch

The number of individual portions assumed to be available within the batch after opening/preparation

8. #Ptns-Total

Displays the total theoretical number of individual portions of the item, obtained by multiplying the #Batches by the #Ptns/Batch, and then adding the #Ptns
Where #Ptns should be seen as service-ready portions, #Ptns-Total provides an estimate of what may be available should all batches be processed into service-ready portions.

9. Prep

Displays weather or not this items "Prep-Flag" has been toggled "on". Prep-Flags are meant to easily mark items that staff believe require preparation, which can then all be easily viewed together once inventory has been completed via Main>Prep, eliminating the need to keep track of items that need to be reviewed for preparation with a second medium, during inventory.

10. Updated

The date that this item was last modified.

11. User

The Username of the last person to update the item

12. Shelf

All items are sorted by shelf; where having a numbering system for a storage unit's individual shelves is preferable, this is not required as "Shelf 0" is added by default. As shelves will be displayed from within the "Prep" and "FIFO" sections, a shelf numbering system may be beneficial for quickly locating any items that have been flagged, physically.

### If an item is within 3 days of it's expiry, it's Name and Expiry will be highlighted in **Yellow**
### If an item is on, or has passed it's expiry, it's Name and Expiry will be highlighted in **Red**

## Cooler/Freezer/Dry - Update:
By opening the hamburger-menu, the user can select the "Update" button to access an editable version of the table.
For each item, the user can update:
1. The Shelf
2. The Production date
3. The Expiry date
4. Number of Portions
5. Number of Batches
6. Number of Portions-per-Batch
7. Prep-Flag status
8. Delete

When the Delete field is toggled to "YES", the row, and all information contained within will be **deleted** upon pressing the submit button.

To avoid accidental inputs, Name and Brand are not updatable fields.
Should a user wish to do so, they should toggle the "Delete" field to "YES", and then use Add Items(below) to re-create the item as a new entry.

###Add Items:

From the "Update" table, users can add new items by navigating to the bottom of the page and clicking the "**+**" icon.
This will generate a new table at the bottom of the page with an empty row for entering the details of the new item.
By default, the Production day will be set to the current date, and Expiry 5 days ahead, making an effective pre-set for most "in-house" items, should they be left unmodified.

A new row will be generated with each subsequent click of the "**+**" icon.

Unlike the Update table's "Delete" toggle, the Add Items table instead has a button, "Discard".
A **Discard** button will **immediately** remove it's parent row, on-click.

###Submit:

The "Submit Update" button is located at the bottom of the "Update" screen.
Once all desired changes have been made to the Update section, and any desired "Add Items" fields created, pressing the "Submit Update" button will update any changes made to the database, add any newly created items, and send the user to a confirmation screen, which will then redirect to the Main Menu.
>Note: It is best to avoid submissions while using a device from the inside of a walk-in unit. Ensure sure there is adequate signal strength before pressing the Submit button

###Created By:

Lewis Fitzsimmons

British Columbia, 
Canada

2022
