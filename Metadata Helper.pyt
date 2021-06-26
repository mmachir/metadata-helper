# -*- coding: utf-8 -*-

import re
import arcpy
import datetime

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Metadata Helper"
        self.alias = "metahelper"

        # List of tool classes associated with this toolbox
        self.tools = [Add_Meta_Fields, Populate_Meta_Fields]
        # additional tools: Populate_Meta_Fields_from_Existing, Populate_Meta_Controls


class Add_Meta_Fields(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Add Meta Fields"
        self.description = "Adds metadata fields to user-defined feature layer(s) from a file geodatabase (.gdb) or Enterprise geodatabase (.sde)."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        # user-defined feature layer(s) from fgdb or egdb
        param0 = arcpy.Parameter(
            displayName="Input feature layer(s)",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        
        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        if parameters[0].value and parameters[0].altered:
            # return list of fcs
            fcs = parameters[0].valueAsText
            fclist = fcs.split(";")
            # return fc field names
            metalist = ['datasetname','datasetid','datetimecreated',
                        'dataowner','datasource','datacontrols']
            wrnm = ""
            errm = ""
            for fc in fclist:
                flist = [f.name for f in arcpy.ListFields(fc) if f.name in metalist]
                if len(flist) == len(metalist):
                    strg = f"{fc} already contains all metadata fields.\n"
                    errm += strg
                elif len(flist) > 0:
                    strg = f"{fc} already contains some of the metadata fields: {', '.join(flist)}\n"
                    wrnm += strg
            if wrnm:
                parameters[0].setWarningMessage(wrnm)
            if errm:
                parameters[0].setErrorMessage(errm)
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # access parameters
        lyrs = parameters[0].valueAsText.split(';')

        # add fields
        for lyr in lyrs:
            arcpy.AddMessage(f"Adding metadata fields to {lyr}...")
            res = arcpy.management.AddFields(
                lyr,
                [['datasetname', 'TEXT', 'Dataset Name', 50, '',''],
                 ['datasetid', 'TEXT', 'Dataset Id', 50, '',''],
                 ['datetimecreated', 'TEXT', 'Dataset Creation Date/Time', 30, '',''],
                 ['dataowner', 'TEXT', 'Dataset Owner', 100, '',''],
                 ['datasource', 'TEXT', 'Dataset Source', 100, '',''],
                 ['datacontrols', 'TEXT', 'Dataset Controls', 255, '','']
                 ])
            arcpy.AddMessage(f"Metadata fields successfully added to {lyr}")
        return

class Populate_Meta_Fields(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Populate Meta Fields"
        self.description = "Populates required metadata fields in user-defined feature layer(s)"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        # user-defined feature layer(s) from fgdb or egdb
        param0 = arcpy.Parameter(
            displayName="Input feature layer(s)",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        
        # select which metadata field(s) to populate
        param1 = arcpy.Parameter(
            displayName="Input Metadata field(s)",
            name="in_fields",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        param1.filter.type = 'ValueList'
        param1.filter.list = ['datasetname','datasetid','datetimecreated','dataowner','datasource']

        param2 = arcpy.Parameter(
            displayName="Dataset Name",
            name="dset",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Dataset Unique Identifier",
            name="ids",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Dataset Ingest Date",
            name="metadate",
            datatype="GPDate",
            parameterType="Optional",
            direction="Input")
        now = datetime.datetime.now()
        today = now.strftime("%m/%d/%y %I:%M:%S %p")
        param4.value = today

        param5 = arcpy.Parameter(
            displayName="Dataset Ingest Time Zone",
            name="tzone",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        param5.filter.type = 'ValueList'
        param5.filter.list = arcpy.time.ListTimeZones()

        param6 = arcpy.Parameter(
            displayName="Dataset Owner",
            name="owner",
            datatype="GPValueTable",
            parameterType="Optional",
            direction="Input")
        param6.columns=[['GPString','Role'],['GPString','Entity']]
        param6.filters[0].type = 'ValueList'
        param6.filters[1].type = 'ValueList'
        param6.values = [['Data Owner','Dept A']]
        param6.filters[0].list = ['Data Owner','Data Custodian','Data Originator']
        param6.filters[1].list = ['Dept A', 'Dept B', 'Dept C']

        param7 = arcpy.Parameter(
            displayName="Dataset Source",
            name="metasrc",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        param7.value = 'ABC1234fakesource.com'

        params = [param0,param1,param2,param3,param4,param5,param6,param7]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if parameters[1].altered:
            flds = parameters[1].valueAsText
            if not flds:
                flds = ''
            if 'datasetname' in flds:
                parameters[2].enabled = True
            else:
                parameters[2].enabled = False
            if 'datasetid' in flds:
                parameters[3].enabled = True
            else:
                parameters[3].enabled = False
            if 'datetimecreated' in flds:
                parameters[4].enabled = True
                parameters[5].enabled = True
            else:
                parameters[4].enabled = False
                parameters[5].enabled = False
            if 'dataowner' in flds:
                parameters[6].enabled = True
            else:
                parameters[6].enabled = False
            if 'datasource' in flds:
                parameters[7].enabled = True
            else:
                parameters[7].enabled = False
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        # set error if user-selected meta fields are not present in input feature layers
        if parameters[0].value and parameters[1].value and parameters[1].altered:
            # return list of fcs
            fcs = parameters[0].valueAsText
            fclist = fcs.split(";")
            # return fc field names
            errm = ""
            for fc in fclist:
                flds = parameters[1].valueAsText.split(";")
                flist = [f.name for f in arcpy.ListFields(fc)]
                xlist = [f.lower() for f in flds if f.lower() not in flist]
                if len(xlist) > 0:
                    xstr = ", ".join(xlist)
                    strg = f"{fc} is missing metadata field(s): {xstr}. Unselect any missing metadata fields below or run the Add Meta Fields tool before proceeding.\n"
                    errm += strg
            if errm:
                parameters[0].setErrorMessage(errm)
        # require additional parameters based on user-selected meta fields
        if parameters[0].value and parameters[1].value and parameters[1].altered:
            flds = parameters[1].valueAsText.split(";")
            if 'datasetname' in flds:
                if not parameters[2].value:
                    parameters[2].setErrorMessage("Required")
            if 'datasetid' in flds:
                if not parameters[3].value:
                    parameters[3].setErrorMessage("Required")
            if 'datetimecreated' in flds:
                if not parameters[4].value:
                    parameters[4].setErrorMessage("Required")
                if not parameters[5].value:
                    parameters[5].setErrorMessage("Required")
            if 'dataowner' in flds:
                if not parameters[6].value:
                    parameters[6].setErrorMessage("Required")
            if 'datasource' in flds:
                if not parameters[7].value:
                    parameters[7].setErrorMessage("Required")
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # access parameters
        lyrs = parameters[0].valueAsText.split(';')
        flds = parameters[1].valueAsText
        nam = parameters[2].valueAsText
        uid = parameters[3].valueAsText
        dtg = parameters[4].valueAsText
        tzn = parameters[5].valueAsText
        ent = parameters[6].valueAsText.split(';')
        src = parameters[7].valueAsText

        # date formatting
        if 'datetimecreated' in flds:
            # get time zone info - user-defined and UTC
            tzinfo = arcpy.time.TimeZoneInfo(tzn)
            utc = arcpy.time.TimeZoneInfo('UTC')
            # apply time zone to user-defined date then convert to UTC
            in_dtg = datetime.datetime.strptime(dtg,'%m/%d/%Y %I:%M:%S %p')
            from_dtg = in_dtg.replace(tzinfo = tzinfo)
            to_utc = from_dtg.astimezone(utc)
            # format date object
            dtformat = datetime.datetime.strftime(to_utc, "%Y-%m-%dT%H:%M:%S.%f")
            dateout = dtformat[:-3]+"Z"

        # entity formatting
        entities = []
        for e in ent:
            rol = e.split(")")[0]
            agc = e[-3:].replace(" ","").replace("'","")
            if 'Custodian' in rol:
                role = 'CUST'
            elif 'Originator' in rol:
                role = 'ORIG'
            elif 'Owner' in rol:
                role = 'OWNR'
            item = f"{role}:meta.{agc}"
            entities.append(item)
        entities.sort(reverse=True)
        entout = ",".join(entities)

        # calculate fields
        popfields = []
        if 'datasetname' in flds:
            fld0 = ['datasetname','"'+nam+'"']
            popfields.append(fld0)
        if 'datasetid' in flds:
            fld1 = ['datasetid','"'+uid+'"']
            popfields.append(fld1)
        if 'datetimecreated' in flds:
            fld2 = ['datetimecreated','"'+dateout+'"']
            popfields.append(fld2)
        if 'dataowner' in flds:
            fld3 = ['dataowner','"'+entout+'"']
            popfields.append(fld3)
        if 'datasource' in flds:
            fld4 = ['datasource','"'+src+'"']
            popfields.append(fld4)

        for lyr in lyrs:
            arcpy.AddMessage(f"Populating metadata fields in {lyr}...")
            arcpy.CalculateFields_management(lyr, "PYTHON3", popfields)
            arcpy.AddMessage(f"Metadata fields successfully populated in {lyr}.")
        return
