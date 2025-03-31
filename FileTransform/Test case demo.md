 Single invoice

# Update the naming “Your QIMA contact”

Note: Apply to all templates(How many template?)


## Step:Generate Invoice

existence data&newly data


### Ex:

#### Display new field

##### Your QIMA contact.png

# New field:'Lab Location Name'

18361:Note: Apply to all templates


## Step:Entrance:Lab Management=>Office=>Edit

## Step:Entrance:Lab Management=>Office=>Add

## Ex

### Between 'Legal Name' & 'Tele No' add 'Lab Location Name' filed

#### Lab Location.png

### The input box length should aline with 'Legal Name'

### The input box can input any character:asdSDF123!@#中文支持

### The input length limit 200：

#### >200 can't save of other warning

#### can be saved while <= 200

### Mandatory validation

#### save without input will pop warning

### Location filed updated successful

#### The invoice should display newly info

# Add a field named “Tel” in office page

Note: Apply to all templates

 
Entrance:Lab Management=>Office=>Edit

 
Entrance:Lab Management=>Office=>Add


## Ex:

### Mandatory validation

#### save without input will pop warning

### Only digit

#### Input other type will give a warning

### Length limit?

### display on invoice top area under 'Lab location'

#### Tel.png

# Remove 'Attendee' field

Note: Apply to all templates

The input entrance?


## Generate Invoice

### Ex:

#### Even the order which this field has data but the invoice should not, In client detail

##### Attendee field remove.png

# Update fields name

Note: Apply to all templates


## Generate Invoice

### Ex:

#### “Accounting” to “Billing”

#####   “Billing” field instead “Accounting”

###### Billing instead.png

####  “Exchange rates” to “Exchange rate(s)”

##### Exchange rates update.png
 
'Other detail' section fields updated

##### Ex:Other detail section should contain below fields and beauty UI

###### Report No.

Service date

Sample description

SKU No.

Client PO No.

Style No.

* Other Detail section.png

# Add 'Turnaround Time' section
 
Generate Invoice


### Ex:
 
Add turnaround section after other detail section


#### The data should come from order test assignments

#### display rule : * + days

# Header:Description
 
Generate Invoice


### Ex:
 
'Description' section update to 'Test Description'


#### The table  of test description section should contain below columns
 
- Test description


 
- Quantity


 
- Special instruction → Align the logic with this ticket:https://qima.atlassian.net/browse/SP-18016


 
- Unit price (USD)


 
- Amount (USD)



#### “Test description” is left-align and the others are horizon-align

# Other header checking
 
Generate Invoice


### Ex:

#### For the header, all of them are vertical-align

#### Note: Apply to all templates
 
'Continue ->'
 
Generate Invoice


### Ex:

#### Multiple page scenario will display

##### Continue button.png

#### Single page scenario?

#### UI checking

# Remove sentence
 
Generate Invoice


### Ex:

#### Remove footer fixed words:This is a computer-generated document. No signature is required.

##### fixed words.png

#### Remove words which under 'Total amount' fields:Say four thousand six hundred sixty eight point eighty three HKD only

##### Remove words.png

#### Note: Apply to all templates

# Total amount section
 
Generate Invoice


### Ex:

#### Surcharge

##### no need to show this line

#### No surcharge

##### If there is a express booking fee, then need to show it “3 Day Express (20% Surcharge)” and its related amount

express fee come from?


#### “Total amount to be paid”: Follow up on the new design

##### total amount UI.png
