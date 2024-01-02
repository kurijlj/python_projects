# =============================================================================
# References
# =============================================================================
#
# * https://nipy.org/nibabel/dicom/dicom_intro.
#   html#dicom-entities-and-information-object-definitions
#
# =============================================================================


# =============================================================================
# Modules Import Section
# =============================================================================
import re

# =============================================================================
# Module Global Variables Declaration Section
# =============================================================================
id_format   = re.compile(r'^-?([0-9\.]*)+[0-9]+$')
name_format = re.compile(r'^[A-Z][A-Za-z]+\^[A-Z][A-Za-z]+$')
date_format = re.compile(r'^\d{8}$')
time_format = re.compile(r'^\d{6}\.\d{6}$')

# =============================================================================
# Class: IENode
# =============================================================================
#
#   Description:
#       This class is used to represent a node in the IENode tree.
#
# =============================================================================
class IENode:
    """TODO: Add class docstring here"""

    # -------------------------------------------------------------------------
    # Class slots
    # -------------------------------------------------------------------------
    __slots__ = ('_node_type', '_node_uid', '_node_key',
                 '_node_attributes', '_node_children')

    # -------------------------------------------------------------------------
    # Class constants
    # -------------------------------------------------------------------------
    TYPES = ('PatientIE', 'StudyIE', 'EquipmentIE',
             'FrameOfReferenceIE', 'SeriesIE', 'ImageIE')

    # -------------------------------------------------------------------------
    # Class methods
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Class properties
    # -------------------------------------------------------------------------
    @property
    def attributes(self):
        return self._node_attributes

    @property
    def children(self):
        return self._node_children

    @property
    def key(self):
        return self._node_key

    @property
    def type(self):
        return self._node_type

    @property
    def uid(self):
        return self._node_attributes[0]
    
    # -------------------------------------------------------------------------
    # Initializer
    # -------------------------------------------------------------------------
    def __init__(self, type: str, uid: str, children: list = []):
        """TODO: Add initializer docstring here"""

        # Validate the type and values of the arguments ------------------------

        # Node type must be one of the types defined in the IENode.TYPES
        if type not in self.TYPES:
            raise ValueError(f'Invalid node type: {type}')
        
        # Node of type Image cannot have children
        if 'ImageIE' == type and bool(children):
            raise ValueError('ImageIE node cannot have children')
        
        # uid must be a string, must not be empty, and must not contain
        # characters other than numbers and dots
        if not isinstance(uid, str):
            raise TypeError('Node uid must be a string')
        if not id_format.match(uid):
            raise ValueError('Invalid node uid')

        # Check if the children are of type IENode and if the children can be
        # added to the node. By definition, a node of type Study can only be
        # child of a node of type PatientIE, a node of type Series can only be
        # child of a node of type Study, and a node of type Image can only be
        # child of a node of type Series.
        for child in children:
            # Children must be of type IENode
            if not isinstance(child, IENode):
                raise TypeError('Invalid child node type')
            # PatientIE can only be root node
            if 'PatientIE' == child.type:
                raise ValueError('PatientIE node cannot be a child node')
            # Equipment can only be a root node
            if 'EquipmentIE' == child.type:
                raise ValueError('EquipmentIE node cannot be a child node')
            # Frame of Reference can only be root node
            if 'FrameOfReferenceIE' == child.type:
                raise ValueError('FrameOfReferenceIE node '\
                                 + 'cannot be a child node')
            # Study can only be child of PatientIE
            if 'PatientIE' == type and 'StudyIE' != child.type:
                raise ValueError('Invalid child node type')
            # Series can only be child of Study
            if 'StudyIE' == type and 'SeriesIE' != child.type:
                raise ValueError('Invalid child node type')
            # Image can only be child of Series
            if 'SeriesIE' == type and 'ImageIE' != child.type:
                raise ValueError('Invalid child node type')

        # Initialize the instance attributes -----------------------------------
        self._node_type = type
        self._node_attributes = (uid,)
        self._node_key = hash((type, uid))
        self._node_children = children

    # -------------------------------------------------------------------------
    # Private methods
    # -------------------------------------------------------------------------
    def __iter__(self):
        return iter(
            (self.type,)\
                + self.attributes\
                + (self.key,)
            )

    def __repr__(self) -> str:
        return '{}({!r}, {!r}, {!r})'\
            .format(self.type, self.uid, self.children)

    def __str__(self) -> str:
        return '{}: {}'.format(self.type, self.uid)
    
    def __bytes__(self) -> bytes:
        raise NotImplementedError(
            'IENode.__bytes__() not implemented'
            )
    
    def __eq__(self, other) -> bool:
        return isinstance(other, IENode) and \
            self.key == other.key

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __bool__(self) -> bool:
        if 'Image' == self.type:
            return False
        else:
            return bool(self.children)
    
    def __len__(self) -> int:
        if 'ImageIE' == self.type:
            return 0
        else:
            return len(self.children)

    def __contains__(self, item) -> bool:
        q = [self]

        while q:
            node = q.pop()
            if node == item:
                return True
            else:
                q.extend(node.children)

    # -------------------------------------------------------------------------
    # Public methods
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Method: hash
    # -------------------------------------------------------------------------
    #
    # Description:
    #   This method returns the hash value of the IENode instance.
    #
    # Parameters:
    #   None
    #
    # Returns:
    #   int
    #
    # -------------------------------------------------------------------------
    def hash(self) -> int:
        """TODO: Add method docstring here"""
        return hash((self.type, self.attributes, self.key)\
                    + tuple(self.children))

    # -------------------------------------------------------------------------
    # Method: find_node
    # -------------------------------------------------------------------------
    #
    # Description:
    #   This method returns the node with the given attributes.
    #
    # Parameters:
    #   attrs: tuple
    #       The attributes of the node to be found.
    #
    # Returns:
    #   IENode
    #       The node with the given attributes.
    #
    # -------------------------------------------------------------------------
    def find_node(self, key: int):
        """TODO: Add method docstring here"""

        q = [self]

        while q:
            node = q.pop()
            if key == node.key:
                return node
            else:
                q.extend(node.children)

        return None

    # -------------------------------------------------------------------------
    # Method: find_parent
    # -------------------------------------------------------------------------
    #
    # Description:
    #   This method returns the parent node of the given node.
    #
    # Parameters:
    #   node: IENode
    #       The node whose parent is to be found.
    #
    # Returns:
    #   IENode
    #       The parent node of the given node.
    #
    # -------------------------------------------------------------------------
    def find_parent(self, node):
        """TODO: Add method docstring here"""
        q = [self]

        while q:
            parent = q.pop()
            if node in parent.children:
                return parent
            else:
                q.extend(parent.children)

        return None

    # -------------------------------------------------------------------------
    # Method: add_child
    # -------------------------------------------------------------------------
    #
    # Description:
    #   This method adds a child node to the given IENode.
    #
    # Parameters:
    #   child: IENode
    #       The child node to be added.
    #
    # Returns:
    #   IENode
    #       The node that was added.
    #
    # -------------------------------------------------------------------------
    def add_child(self, child):
        """TODO: Add method docstring here"""

        if not isinstance(child, IENode):
            raise TypeError('Invalid child node type')
        if 'PatientIE' == self.type and 'StudyIE' != child.type:
            raise ValueError(
                '{} node cannot be a child of PatientIE'.format(child.type)
                )
        if 'StudyIE' == self.type and 'SeriesIE' != child.type:
            raise ValueError(
                '{} node cannot be a child of StudyIE'.format(child.type)
                )
        if 'SeriesIE' == self.type and 'ImageIE' != child.type:
            raise ValueError(
                '{} node cannot be a child of SeriesIE'.format(child.type)
                )
        
        # Assure that the child node is not already a child of the given parent
        # node.
        if child in self.children:
            return None
        
        self._node_children.append(child)

        return child

    # -------------------------------------------------------------------------
    # Method: remove_child
    # -------------------------------------------------------------------------
    #
    # Description:
    #   This method removes a child from the given IENode.
    #
    # Parameters:
    #   node: IENode
    #       The node to be removed.
    #
    # Returns:
    #   IENode
    #       The node that was removed.
    #
    # -------------------------------------------------------------------------
    def remove_node(self, node):
        """TODO: Add method docstring here"""
            
        if not isinstance(node, IENode):
            raise TypeError('Invalid child node type')

        if node not in self.children:
            return None
    
        self.__node_children.remove(node)  # TODO: Check if this works and if
                                        # it is the best way to do it
        return node
    
    # -------------------------------------------------------------------------
    # Method: set_node
    # -------------------------------------------------------------------------
    #
    # Description:
    #   This method replaces a node with the given attributes with the given
    #   replacement node.
    #
    # Parameters:
    #   attrs: tuple
    #       The attributes of the node to be replaced.
    #   replacement: IENode
    #       The replacement node.
    #
    # Returns:
    #   IENode
    #       The node that was replaced.
    #
    # -------------------------------------------------------------------------
    def set_node(self, key: int, replacement):
        """TODO: Add method docstring here"""

        if not isinstance(replacement, IENode):
            raise TypeError('Replacement node must be of type IENode')

        for index, item in enumerate(self.__node_children):
            if key == item.key:
                self.__node_children[index] = replacement
                return item
        
        return None

    # -------------------------------------------------------------------------
    # Method: print_tree
    # -------------------------------------------------------------------------
    #
    # Description:
    #   This method prints the IENode tree.
    #
    # Parameters:
    #   marker: str
    #       The marker to be used to print the tree.
    #
    # Returns:
    #   None
    #
    # -------------------------------------------------------------------------
    def print_tree(self, marker: str = "+- "):
        """TODO: Put the function docstring here."""

        empty_spc = ' '*len(marker)
        connection = '|' + empty_spc[:-1]
        prefix = ['']

        queue = [self]
        root_depth = IENode.TYPES.index(self.type)

        while queue:
            current = queue.pop(0)
            current_depth = IENode.TYPES.index(current.type)\
                - root_depth
            if current_depth < len(prefix):                 
                prefix = prefix[:current_depth]
            if 0 == len(queue) or \
                    IENode.TYPES.index(queue[0].type) < \
                    IENode.TYPES.index(current.type):
                if 0 == current_depth:
                    connection = ''
                else:
                    connection = empty_spc
            else:
                connection = '|' + empty_spc[:-1]

            prefix.append(connection)

            if 0 == current_depth:
                print('{}'.format(current))
            else:
                print('{}{}{}'.format(''.join(prefix[:-1]), marker, current))

            queue = current.children + queue


# =============================================================================
# Class: PatientIE
# =============================================================================
#
#   Description:
#       This class is used to represent a patient in the IENode tree.
#
# =============================================================================
class PatientIE(IENode):
    """TODO: Add class docstring here"""

    # -------------------------------------------------------------------------
    # Class constants
    # -------------------------------------------------------------------------
    TYPE = 'PatientIE'
    PATIENT_ID_TYPE = ['TEXT', 'RFID', 'BARCODE']
    PATIENT_SEX = ['M', 'F', 'O']

    # -------------------------------------------------------------------------
    # Class properties
    # -------------------------------------------------------------------------
    @property
    def PatientName(self):
        return self._node_attributes[2]

    @property
    def PatientID(self):
        return self._node_attributes[0]
    
    @property
    def PatientBirthDate(self):
        return self._node_attributes[3]

    @property
    def PatientSex(self):
        return self._node_attributes[5]
    
    @property
    def TypeOfPatientID(self):
        return self._node_attributes[1]

    @property
    def PatientSpeciesDescription(self):
        return self._node_attributes[4]
    
    @property
    def QualityControlSubject(self):
        return self._node_attributes[6]

    # -------------------------------------------------------------------------
    # Initializer
    # -------------------------------------------------------------------------
    def __init__(
            self,
            name: str,
            uid: str,
            birth_date: str = '19000101',
            sex: str = 'M',
            uid_type: str = 'TEXT',
            species_desc: str = 'HUMAN',
            qa_subject: bool = False,
            children: list = []
            ):
        """TODO: Add initializer docstring here"""

        # Validate the type and values of the arguments ------------------------

        # Patient name must be a string, must not be empty, and must be in the
        # format "Last^First"
        if not isinstance(name, str):
            raise TypeError('Patient name must be a string')
        if not name_format.match(name):
            raise ValueError('Invalid patient name')
        
        # Patient ID must be a string, must not be empty, and must not contain
        # characters other than numbers and dots
        if not isinstance(uid, str):
            raise TypeError('Patient ID must be a string')
        if not id_format.match(uid):
            raise ValueError('Invalid patient ID')
        
        # Patient birth date must be a string, must not be empty, and must be
        # in the format YYYYMMDD, where YYYY is the year, MM is the month, and
        # DD is the day. The year must be greater than 1900, the month must be
        # between 1 and 12, and the day must be between 1 and 31.
        if not isinstance(birth_date, str):
            raise TypeError('Patient birth date must be a string')
        if not date_format.match(birth_date):
            raise ValueError('Invalid patient birth date')
        if 1900 > int(birth_date[0:4]):
            raise ValueError('Invalid Birth Year')
        if 1 > int(birth_date[4:6]) or 12 < int(birth_date[4:6]):
            raise ValueError('Invalid Birth Month')
        if 1 > int(birth_date[6:8]) or 31 < int(birth_date[6:8]):
            raise ValueError('Invalid Birth Day')

        # Patient sex must be a string, must not be empty, and must be one of
        # the values defined in the Patient.PATIENT_SEX list
        if sex not in self.PATIENT_SEX:
            raise ValueError('Invalid patient sex')
        
        # Patient ID type must be a string, must not be empty, and must be one
        # of the values defined in the Patient.PATIENT_ID_TYPE list
        if uid_type not in self.PATIENT_ID_TYPE:
            raise ValueError('Invalid patient ID type')

        # Patient species description must be a string and must not be empty.
        if not isinstance(species_desc, str) or not species_desc:
            raise TypeError('Patient species description must be '\
                            + 'a non empty string')

        # Quality control subject must be a boolean value. It is converted to
        # a string value ('YES'/'NO') before being stored in the node
        # attributes (for compatibility with the DICOM standard)
        if not isinstance(qa_subject, bool):
            raise TypeError('Quality control subject must be a boolean')

        super().__init__(self.TYPE, str(hash(f'{name} {uid}')), children)
        
        # Initialize the instance attributes -----------------------------------
        self._node_attributes = (
                uid,
                uid_type,
                name,
                birth_date,
                species_desc,
                sex,
                'YES' if qa_subject else 'NO'
                )
    
    # -------------------------------------------------------------------------
    # Private methods
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        return '{}({!r}, {!r}, {!r}, {!r}, {!r})'.format(
                self.type,
                self.attributes[2],  # Patient Name
                self.uid,
                self.attributes[3],  # Patient Birth Date
                self.attributes[5],  # Ptient Sex
                '[...]' if self.children else '[]'
                )

    def __str__(self) -> str:
        return '{}: {} ({}) {}'.format(
                self.type,
                self.attributes[2],  # Patient Name
                self.attributes[5],  # Ptient Sex
                self.attributes[3]   # Patient Birth Date
                )
    

# =============================================================================
# Class: EquipmentIE
# =============================================================================
#
#   Description:
#       This class is used to represent an equipment in the IENode tree.
#
# =============================================================================
class EquipmentIE(IENode):
    """TODO: Add class docstring here"""

    # -------------------------------------------------------------------------
    # Class constants
    # -------------------------------------------------------------------------
    TYPE = 'EquipmentIE'

    # -------------------------------------------------------------------------
    # Class properties
    # -------------------------------------------------------------------------
    @property
    def Manufacturer(self):
        return self._node_attributes[0]
    
    @property
    def InstitutionName(self):
        return self._node_attributes[1]
    
    @property
    def InstitutionAddress(self):
        return self._node_attributes[2]
    
    @property
    def StationName(self):
        return self._node_attributes[3]
    
    @property
    def ManufacturerModelName(self):
        return self._node_attributes[4]
    
    @property
    def SoftwareVersions(self):
        return self._node_attributes[5]

    # -------------------------------------------------------------------------
    # Initializer
    # -------------------------------------------------------------------------
    def __init__(
            self,
            manufacturer: str,
            institution_name: str,
            institution_address: str,
            station_name: str,
            manufacturer_model_name: str,
            software_versions: str,
            ):
        """TODO: Add initializer docstring here"""

        # Validate the type and values of the arguments --------------------

        # Manufacturer must be a string and must not be empty.
        if not isinstance(manufacturer, str) and not manufacturer:
            raise TypeError('Manufacturer must be a non empty string')
        
        # Institution Name must be a string and must not be empty.
        if not isinstance(institution_name, str) and not institution_name:
            raise TypeError('Institution Name must be a non empty string')
        
        # Institution Address must be a string and must not be empty.
        if not isinstance(institution_address, str)\
                and not institution_address:
            raise TypeError('Institution Address must be '\
                            + 'a non empty string')

        # Station Name must be a string and must not be empty.
        if not isinstance(station_name, str) and not station_name:
            raise TypeError('Station Name must be a non empty string')
        
        # Manufacturer Model Name must be a string and must not be empty.
        if not isinstance(manufacturer_model_name, str)\
                and not manufacturer_model_name:
            raise TypeError('Manufacturer Model Name must be '\
                            + 'a non empty string')
        
        # Software Versions must be a string and must not be empty.
        if not isinstance(software_versions, str)\
                and not software_versions:
            raise TypeError('Software Versions must be '\
                            + 'a non empty string')
        
        super().__init__(
                self.TYPE,
                str(hash(f'{manufacturer} {manufacturer_model_name} '\
                          + f'{software_versions}')),
                []
                )
            
        # Initialize the instance attributes -------------------------------
        self._node_attributes = (
            manufacturer,
            institution_name,
            institution_address,
            station_name,
            manufacturer_model_name,
            software_versions
            )
            
    # -------------------------------------------------------------------------
    # Private methods
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        return '{}({!r} {!r} {!r})'.format(
                self.type,
                self.attributes[0],  # Manufacturer
                self.attributes[4],  # Manufacturer Model Name
                self.attributes[5]   # Software Versions
                )
    
    def __str__(self) -> str:
        return '{}: {} {} {}'.format(
                self.type,
                self.attributes[0],  # Manufacturer
                self.attributes[4],  # Manufacturer Model Name
                self.attributes[5]   # Software Versions
                )


# =============================================================================
# Class: FrameOfReferenceIE
# =============================================================================
#
#   Description:
#       This class is used to represent a frame of reference in the IENode
#       tree.
#
# =============================================================================
class FrameOfReferenceIE(IENode):
    """TODO: Add class docstring here"""

    # -------------------------------------------------------------------------
    # Class constants
    # -------------------------------------------------------------------------
    TYPE = 'FrameOfReferenceIE'

    # -------------------------------------------------------------------------
    # Class properties
    # -------------------------------------------------------------------------
    @property
    def attributes(self):
        return self._node_attributes
    
    @property
    def FrameOfReferenceUID(self):
        return self._node_attributes[0]
    
    @property
    def PositionReferenceIndicator(self):
        return self._node_attributes[1]

    # -------------------------------------------------------------------------
    # Initializer
    # -------------------------------------------------------------------------
    def __init__(
            self,
            uid: str,
            position_reference_indicator: str,
            ):
        """TODO: Add initializer docstring here"""

        # Validate the type and values of the arguments --------------------

        # Frame of Reference UID must be a string, must not be empty, and must
        # not contain characters other than numbers and dots.
        if not isinstance(uid, str):
            raise TypeError('Frame of Reference UID must be a string')
        if not id_format.match(uid):
            raise ValueError('Invalid Frame of Reference UID')
        
        # Position Reference Indicator must be a string and must not be empty.
        if not isinstance(position_reference_indicator, str)\
                and not position_reference_indicator:
            raise TypeError('Position Reference Indicator must be '\
                            + 'a non empty string')

        super().__init__(self.TYPE, uid, [])

        # Initialize the instance attributes -------------------------------
        self._node_attributes = (
            uid,
            position_reference_indicator,
            )
        
    # -------------------------------------------------------------------------
    # Private methods
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        return '{}({!r}, {!r})'.format(
                self.type,
                self.uid,
                self.PositionReferenceIndicator
                )
    
    def __str__(self) -> str:
        return '{}: {}'.format(
                self.type,
                self.attributes[1]   # Position Reference Indicator
                )


# =============================================================================
# Class: StudyIE
# =============================================================================
#
#   Description:
#       This class is used to represent a study in the IENode tree.
#
# =============================================================================
class StudyIE(IENode):
    """TODO: Add class docstring here"""

    # -------------------------------------------------------------------------
    # Class constants
    # -------------------------------------------------------------------------
    TYPE = 'StudyIE'

    # -------------------------------------------------------------------------
    # Class properties
    # -------------------------------------------------------------------------
    @property
    def StudyInstanceUID(self):
        return self._node_attributes[0]
    
    @property
    def StudyID(self):
        return self._node_attributes[1]
    
    @property
    def StudyDescription(self):
        return self._node_attributes[2]
    
    @property
    def StudyDate(self):
        return self._node_attributes[3]
    
    @property
    def StudyTime(self):
        return self._node_attributes[4]

    @property
    def AccessionNumber(self):
        return self._node_attributes[5]
    
    @property
    def ReferringPhysicianName(self):
        return self._node_attributes[6]

    # -------------------------------------------------------------------------
    # Initializer
    # -------------------------------------------------------------------------
    def __init__(
            self,
            uid: str,
            study_id: str,
            study_desc: str,
            study_date: str,
            study_time: str,
            accession_number: str,
            referring_physician_name: str,
            equipment: EquipmentIE,
            frame_of_reference: FrameOfReferenceIE,
            children: list[IENode] = []
            ):
        """TODO: Add initializer docstring here"""

        # Validate the type and values of the arguments --------------------

        # Study Instance UID must be a string, must not be empty, and must not
        # contain characters other than numbers and dots. We use a SOP Instance
        # UID as a Study Instance UID.
        if not isinstance(uid, str):
            raise TypeError('Study Instance UID must be a string')
        if not id_format.match(uid):
            raise ValueError('Invalid Study Instance UID')
        
        # Study ID must be a string, must not be empty, and must not contain
        # characters other than numbers and dots. Generaly speaking, a Study ID
        # can be any combination of characters, but we use study date and time
        # as a Study ID (in the format YYYYMMDDHHMMSS).
        if not isinstance(study_id, str):
            raise TypeError('Study ID must be a string')
        if not id_format.match(study_id):
            raise ValueError('Invalid Study ID')

        # Study Description must be a string and must not be empty.
        if not isinstance(study_desc, str) and not study_desc:
            raise TypeError('Study Description must be a non empty string')

        # Study Date must be a string, must not be empty, and must be in the
        # format YYYYMMDD, where YYYY is the year, MM is the month, and DD is
        # the day. The year must be greater than 1900, the month must be
        # between 1 and 12, and the day must be between 1 and 31.
        if not isinstance(study_date, str):
            raise TypeError('Study Date must be a string')
        if not date_format.match(study_date):
            raise ValueError('Invalid Study Date')
        if 1900 > int(study_date[0:4]):
            raise ValueError('Invalid Study Year')
        if 1 > int(study_date[4:6]) or 12 < int(study_date[4:6]):
            raise ValueError('Invalid Study Month')
        if 1 > int(study_date[6:8]) or 31 < int(study_date[6:8]):
            raise ValueError('Invalid Study Day')

        # Study Time must be a string, must not be empty, and must be in the
        # format HHMMSS.SSSSSS, where HH is the hour, MM is the minute, SS is
        # the second, and SSSSSS is the fraction of the second. The hour must
        # be between 0 and 23, the minute must be between 0 and 59, the second
        # must be between 0 and 59, and the fraction of the second must be
        # between 0 and 999999.
        if not isinstance(study_time, str):
            raise TypeError('Study Time must be a string')
        if not time_format.match(study_time):
            raise ValueError('Invalid Study Time')
        if 0 > int(study_time[0:2]) or 23 < int(study_time[0:2]):
            raise ValueError('Invalid Study Hour')
        if 0 > int(study_time[2:4]) or 59 < int(study_time[2:4]):
            raise ValueError('Invalid Study Minute')
        if 0 > int(study_time[4:6]) or 59 < int(study_time[4:6]):
            raise ValueError('Invalid Study Second')
        if 0 > int(study_time[7:12]) or 999999 < int(study_time[7:12]):
            raise ValueError('Invalid Study Fraction of Second')

        # Accession Number must be a string and must not be empty. Generaly
        # we use "1" as an Accession Number.
        if not isinstance(accession_number, str):
            raise TypeError('Accession Number must be a string')
        
        # Referring Physician Name must be a string and must not be empty.
        if not isinstance(referring_physician_name, str):
            raise TypeError('Referring Physician Name must be a string')
        
        # Equipment must be an instance of the EquipmentIE class.
        if not isinstance(equipment, EquipmentIE):
            raise TypeError('Invalid EquipmentIE instance')
        
        # Frame of Reference must be an instance of the FrameOfReferenceIE
        # class.
        if not isinstance(frame_of_reference, FrameOfReferenceIE):
            raise TypeError('Invalid FrameOfReferenceIE instance')

        super().__init__(self.TYPE, uid, children)
        
        # Initialize the instance attributes -----------------------------------
        self._node_attributes = (
                uid,
                study_id,
                study_desc,
                study_date,
                study_time,
                accession_number,
                referring_physician_name,
                equipment,
                frame_of_reference
                )
        
    # -------------------------------------------------------------------------
    # Private methods
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        class_name = type(self).__name__
        return '{}({!r}, {!r}, {!r}, {!r})'.format(
                self.type,
                self.uid,
                self.attributes[7],  # Equipment
                self.attributes[8],  # Frame of Reference
                '[...]' if self.children else '[]'
                )

    def __str__(self) -> str:
        #return str(tuple(self))
        return '{}: {} {}, {}, {}'.format(
                self.type,
                self.attributes[2],  # Study Description
                self.attributes[1],  # Study ID
                self.attributes[3],  # Study Date
                self.attributes[4]  # Study Time
                )


# =============================================================================
# Class: SeriesIE
# =============================================================================
#
#   Description:
#       This class is used to represent a series in the IENode tree.
#
# =============================================================================
class SeriesIE(IENode):
    """TODO: Add class docstring here"""

    # -------------------------------------------------------------------------
    # Class constants
    # -------------------------------------------------------------------------
    TYPE = 'SeriesIE'
    MODALITY = ['CT', 'MR']  # TODO: Add more modalities
    PATIENT_POSITION = ['HFS', 'HFP', 'FFS', 'FFP', 'HFDR', 'HFDL', 'FFDR',
                        'FFDL', 'AFDR', 'AFDL', 'UNDEFINED']

    # -------------------------------------------------------------------------
    # Class properties
    # -------------------------------------------------------------------------
    @property
    def SeriesInstanceUID(self):
        return self._node_attributes[0]
    
    @property
    def SeriesNumber(self):
        return self._node_attributes[1]
    
    @property
    def SeriesDescription(self):
        return self._node_attributes[2]
    
    @property
    def Modality(self):
        return self._node_attributes[3]
    
    @property
    def SeriesDate(self):
        return self._node_attributes[4]
    
    @property
    def SeriesTime(self):
        return self._node_attributes[5]
    
    @property
    def BodyPartExamined(self):
        return self._node_attributes[6]
    
    @property
    def PatientPosition(self):
        return self._node_attributes[7]

    # -------------------------------------------------------------------------
    # Initializer
    # -------------------------------------------------------------------------
    def __init__(
            self,
            uid: str,
            series_number: str,
            series_desc: str,
            modality: str,
            series_date: str,
            series_time: str,
            body_part_examined: str,
            patient_position: str,
            children: list[IENode] = []
            ):
        """TODO: Add initializer docstring here"""

        # Validate the type and values of the arguments --------------------

        # Series Instance UID must be a string, must not be empty, and must not
        # contain characters other than numbers and dots. We use a SOP Instance
        # UID as a Series Instance UID.
        if not isinstance(uid, str):
            raise TypeError('Series Instance UID must be a string')
        if not id_format.match(uid):
            raise ValueError('Invalid Series Instance UID')
        
        # Series Number must be a string, must not be empty, and must not
        # contain characters other than numbers and dots. Generaly speaking, a
        # Series Number can be any combination of characters, but we use study
        # date and time as a Series Number (in the format YYYYMMDDHHMMSS).
        if not isinstance(series_number, str):
            raise TypeError('Series Number must be a string')
        
        # Series Description must be a string and must not be empty.
        if not isinstance(series_desc, str) and not series_desc:
            raise TypeError('Series Description must be a non empty string')
        
        # Modality must be a string, must not be empty and must be one of the
        # values defined in the Series.MODALITY list.
        if modality not in self.MODALITY:
            raise ValueError('Invalid modality')
        
        # Series Date must be a string, must not be empty, and must be in the
        # format YYYYMMDD, where YYYY is the year, MM is the month, and DD is
        # the day. The year must be greater than 1900, the month must be
        # between 1 and 12, and the day must be between 1 and 31.
        if not isinstance(series_date, str):
            raise TypeError('Series Date must be a string')
        if not date_format.match(series_date):
            raise ValueError('Invalid Series Date')
        if 1900 > int(series_date[0:4]):
            raise ValueError('Invalid Series Year')
        if 1 > int(series_date[4:6]) or 12 < int(series_date[4:6]):
            raise ValueError('Invalid Series Month')
        if 1 > int(series_date[6:8]) or 31 < int(series_date[6:8]):
            raise ValueError('Invalid Series Day')
        
        # Series Time must be a string, must not be empty, and must be in the
        # format HHMMSS.SSSSSS, where HH is the hour, MM is the minute, SS is
        # the second, and SSSSSS is the fraction of the second. The hour must
        # be between 0 and 23, the minute must be between 0 and 59, the second
        # must be between 0 and 59, and the fraction of the second must be
        # between 0 and 999999.
        if not isinstance(series_time, str):
            raise TypeError('Series Time must be a string')
        if not time_format.match(series_time):
            raise ValueError('Invalid Series Time')
        if 0 > int(series_time[0:2]) or 23 < int(series_time[0:2]):
            raise ValueError('Invalid Series Hour')
        if 0 > int(series_time[2:4]) or 59 < int(series_time[2:4]):
            raise ValueError('Invalid Series Minute')
        if 0 > int(series_time[4:6]) or 59 < int(series_time[4:6]):
            raise ValueError('Invalid Series Second')
        if 0 > int(series_time[7:12]) or 999999 < int(series_time[7:12]):
            raise ValueError('Invalid Series Fraction of Second')
        
        # Body Part Examined must be a string and must not be empty.
        if not isinstance(body_part_examined, str)\
                and not body_part_examined:
            raise TypeError('Body Part Examined must be '\
                            + 'a non empty string')
        
        # Patient Position must be a string, must not be empty and must be one
        # of the values defined in the Series.PATIENT_POSITION list.
        if patient_position not in self.PATIENT_POSITION:
            raise ValueError('Invalid patient position')
        
        super().__init__(self.TYPE, uid, children)

        # Initialize the instance attributes -------------------------------
        self._node_attributes = (
                uid,
                series_number,
                series_desc,
                modality,
                series_date,
                series_time,
                body_part_examined,
                patient_position,
                )


# =============================================================================
# Function: main
# =============================================================================
#
# Description:
#   The main function defines the unit tests for the IENode class.
#
# =============================================================================
if __name__ == '__main__':
    patient1 = PatientIE(
            'Phantom^Synthetic',
            '01011900001001',
            '19000101',
            'O',
            'TEXT',
            'PHANTOM',
            True
            )
    patient2 = PatientIE(
            'John^Smith',
            '01011900001002',
            '19000101',
            'M',
            'TEXT',
            'HUMAN',
            False
            )
    patient3 = PatientIE(
            'Jane^Smith',
            '01011900001003',
            '19000101',
            'F',
            'TEXT',
            'HUMAN',
            False
            )
    patient4 = PatientIE(
            'Virtual^Phantom',
            '01011900001001',
            '19000101',
            'O',
            'TEXT',
            'PHANTOM',
            True
            )
    
    print(patient1)
    print('\t{}'.format(patient1.PatientName))
    print('\t{}'.format(patient1.PatientID))
    print('\t{}'.format(patient1.TypeOfPatientID))
    print('\t{}'.format(patient1.PatientBirthDate))
    print('\t{}'.format(patient1.PatientSex))
    print('\t{}'.format(patient1.PatientSpeciesDescription))
    print('\t{}'.format(patient1.QualityControlSubject))
    print(patient1.__repr__())
    print(patient2)
    print(patient3)
    print(patient4)
    print('patient1 == patient1: ', patient1 == patient1)
    print('patient1 == patient2: ', patient1 == patient2)
    print('patient1 == patient3: ', patient1 == patient3)
    print('patient1 == patient4: ', patient1 == patient4)
    print('patient2 == patient2: ', patient2 == patient2)
    print('patient2 == patient3: ', patient2 == patient3)
    print('patient2 == patient4: ', patient2 == patient4)
    print('patient3 == patient3: ', patient3 == patient3)
    print('patient3 == patient4: ', patient3 == patient4)
    print('patient4 == patient4: ', patient4 == patient4)

    equipment = EquipmentIE(
            'Infinitum Solutions',
            'Infinitum Clinic',
            'Nowhere Blvd. 123',
            'Virtual Workstation',
            'Virtual Phantom',
            '1.0.0'
            )
    print(equipment)

    frame_of_reference = FrameOfReferenceIE(
            '1.2.840.10008.123456789.1.1',
            'PHANTOM_CENTER'
            )
    print(frame_of_reference)

    study1 = StudyIE(
            '1.2.840.10008.123456789.1.1',
            '20210101120000',
            'Study 1',
            '20210101',
            '120000.000000',
            '1',
            'Dr. John Smith',
            equipment,
            frame_of_reference
            )
    study2 = StudyIE(
            '1.2.840.10008.123456789.1.2',
            '20210101120001',
            'Study 2',
            '20210101',
            '120001.000000',
            '2',
            'Dr. Jane Smith',
            equipment,
            frame_of_reference
            )
    print(study1)
    print('\t{}'.format(study1.StudyInstanceUID))
    print('\t{}'.format(study1.StudyID))
    print('\t{}'.format(study1.StudyDescription))
    print('\t{}'.format(study1.StudyDate))
    print('\t{}'.format(study1.StudyTime))
    print('\t{}'.format(study1.AccessionNumber))
    print('\t{}'.format(study1.ReferringPhysicianName))
    print(study1.__repr__())
    print(study2)
    print('study1 == study1: ', study1 == study1)
    print('study1 == study2: ', study1 == study2)
    print('study2 == study2: ', study2 == study2)

    patient1.add_child(study1)
    patient1.add_child(study2)
    print(patient1)
    patient1.print_tree()