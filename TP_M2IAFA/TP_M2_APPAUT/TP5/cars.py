# module de lecture/parsing données images dataset cars

brand_dict = {0: 'Audi', 1: 'BMW', 2: 'Chevrolet', 3: 'Dodge', 4: 'Ford', 5: 'Other'}
vehicle_types_dict = {0: 'Convertible', 1: 'Coupe', 2: 'SUV', 3: 'Van', 4: 'Other'}

import numpy as np
import scipy.io

class MetaParsing():
      '''
      Class for parsing image and meta-data for the Stanford car dataset to create a custom dataset.
      path: The filepah to the metadata in .mat format.
      *args: Accepts dictionaries with self-created labels which will be extracted from the metadata 
      (e.g. {0: 'Audi', 1: 'BMW', 3: 'Other').
      year: Can be defined to create two classes (<=year and later).
      '''
      def __init__(self,path,*args,year=None):
        self.mat = scipy.io.loadmat(path)
        self.year = year
        self.args = args
        self.annotations = np.transpose(self.mat['annotations'])
        #Extracting the file name for each sample
        self.file_names = [annotation[0][0][0].split("/")[-1] for annotation in self.annotations]
        #Extracting the index of the label for each sample
        self.label_indices = [annotation[0][5][0][0] for annotation in self.annotations]
        #Extracting the car names as strings
        self.car_names = [x[0] for x in self.mat['class_names'][0]]
        #Create a list with car names instead of label indices for each sample
        self.translated_car_names = [self.car_names[x-1] for x in self.label_indices]
        
      def brand_types(self,base_dict, x):
        y = list(base_dict.keys())[-1]
        for k,v in base_dict.items():
          if v in x: y=k
        return y
    
      def parsing(self):
        result = []
        for arg in self.args:
          temp_list = [self.brand_types(arg,x) for x in self.translated_car_names]
          result.append(temp_list)
        if self.year != None:
          years_list = [0 if int(x.split(" ")[-1]) <= self.year else 1 for x in self.translated_car_names]
          result.append(years_list)
        brands = [x.split(" ")[0] for x in self.translated_car_names]
        return result, self.file_names, self.translated_car_names



def load_annotations(annotation_path="./Car_dataset/cars_annos.mat"):
    results, file_names, translated_car_names = MetaParsing(annotation_path,brand_dict,vehicle_types_dict,year=2009).parsing()
    translation_dict = dict(zip(file_names,list(zip(results[0],results[1],results[2]))))
    return translation_dict