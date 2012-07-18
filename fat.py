import struct

class bootrec(dict):
    '''This class will convert the charector buffer of size 512 bytes to
    the fat32 boot record + extended boot rectord'''
    def __init__(self,bootsect):
        self.unpack_str = "<3s8shBhBhhBhhhiiihhihh12xBBBi11s8s420x2s"
        self.key_tuple = ('jump_inst','oem_id','Bytes_sector','Sector_cluster',
                          'NReserved_sector','NFats','NDentry','TotSect',
                          'Media_Type','Sectors_FAT','Sectors_Track',
                          'Nheads','Hidden_Sect','LargesectFlag','Sect_FAT32',
                          'Flags','verNo','rootClusterNo','FSINFOClusterNO',
                          'backupBootSector','DriveNo','Flag2','Signature',
                          'volID','VolLabel','systemID','sign2')
        self.tuple = struct.unpack(self.unpack_str,bootsect)
        count = 0
        for i in self.key_tuple:
            self[i] = self.tuple[count]
            count = count + 1
    def first(self):
        return (self["NReserved_sector"] + (self["NFats"] * self["Sect_FAT32"]))*self["Bytes_sector"]

    def clus(self,n):
        return ((n-2) * self['Sector_cluster'] * self["Bytes_sector"]) + self.first()

    def showall(self):
        for i,j in self.items():
            print i,":",j

class DirEntry(dict):
    '''This class will format the charector buffer of size 32 
    To the format of fat32 directory entry'''
    def __init__(self,dirEntry):
        self.unpack_str = "<B10sBBBhhhhhhhi"
        self.key_tuple = ("first_char","name","attribues","reserved","create_tim_sec",
                      "crate_tim","create_date","last_acc_date",
                      "high_16","last_modification_time",
                      "last_modifiation_date","low_16","size")
        self.tuple = struct.unpack(self.unpack_str,dirEntry)
        count = 0
        for i in self.key_tuple:
            self[i] = self.tuple[count]
            count = count + 1
    
    def showall(self):
        for i,j in self.items():
            print i,":",j

class LongDirEntry(dict):
    '''This class will format the charector buffer given to 
    To the format of long directory entrys'''
    def __init__(self,buffer):
        self.unpack_str = "<B10sBBB12shi"
        self.key_tuple = ("sequence_no","first_five_char","attribute","reserv",
                          "checksum","next_six_char","clust_start","last_2_ch")
        self.tuple = struct.unpack(self.unpack_str,buffer)
        count = 0
        for i in self.key_tuple:
            self[i] = self.tuple[count]
            count = count + 1

    def showall(self):
        for i,j in self.items():
            print i,":",j
    
    def return_size(self):
        return struct.calcsize(self.unpack_str)

def main():
    fd = open('fat','r')
    bootsect = fd.read(512)
    BootRec = bootrec(bootsect)
    BootRec.showall()
    fd.seek((BootRec["NReserved_sector"] + (BootRec["NFats"] * BootRec["Sect_FAT32"]))*BootRec["Bytes_sector"])
    root_sect = fd.read(512)
    flag = 0
    for i in range(512):
        j = i*64
        k = j + 32
        l = k + 32
        print 'i:',i,'j:',j,'l:',l
        print '-------------long dir entry--------------'
        dirent = LongDirEntry(root_sect[j:k])
        dirent.showall()
        print '-------------dir entry------------------'
        dirent = DirEntry(root_sect[k:l])
        if dirent['first_char'] == 0xE5:
            print dirent['name'],"1 is unallocated"
        elif dirent['first_char'] == 0x00:
            dirent.showall()
            break
        else:
            val = dirent['high_16'] << 16 | dirent['low_16']
            print "val is ",val
            if val > 0:
                print 'clus value is',BootRec.clus(val)
                fd.seek(BootRec.clus(val))
                print fd.read(512)
                dirent.showall()
main()
