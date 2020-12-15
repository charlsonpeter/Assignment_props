from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.views import View
import pandas as pd
import requests
import os
# Create your views here.


class AddressView(View):
    template_name = 'Uploading.html'
    """Loading Template"""
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        """Upload address file and return updated file"""
        try:
            fle_file = request.FILES.get('addressfile')
            df = pd.read_excel(fle_file,header=0)
            df_address = df.get('address', df.get('Address', df.get('ADDRESS')))
            if not df_address.empty:
                lst_address = df_address.tolist() # create address list
            else:
                return HttpResponse('Address not found')

            lst_address = [adrs.replace(" ","+") for adrs in lst_address]
            str_address = ",".join(lst_address)
            GOOGLE_API_URL = "https://maps.googleapis.com/maps/api/geocode/json?ddress="+str_address+"&key="+ settings.GOOGLE_GEOCODE_KEY # google geocode api url
            lst_latitude = []
            lst_longitude = []
            dct_location_data = {}
            try:
                api_response = requests.get(url=GOOGLE_API_URL.format(str_address)) # geocode API call
                dct_response = api_response.json()
                if dct_response:
                    for dct_data in dct_response['results']:
                        dct_location_data[dct_data['geometry']['formatted_address']] = {'Latitude': dct_data['geometry']['location']['lat'], 'Longitude': dct_data['geometry']['location']['lng']} # creating dictionary for address eith latitude and longitude
            except Exception:
                return HttpResponse('Something went wrong')
            for address in lst_address:
                lst_latitude.append(dct_location_data.get(address.replace(" ","+")).get('Latitude','')) # create a list of latitude for data frame corresponding address
                lst_longitude.append(dct_location_data.get(address.replace(" ","+")).get('Longitude','')) # create a list of latitude for data frame corresponding address
            df['Latitude'] = lst_latitude # assign latitude list to data frame
            df['Longitude'] = lst_longitude # assign longitude list to data frame

            file_path = settings.MEDIA_ROOT+'/Address.xlsx'
            df.to_excel(file_path, index=False) # to create xlsx file with latitude and longitude

            """return updated file"""
            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                    return response

            return HttpResponse('Failed')
        except Exception as e:
            return HttpResponse('Something went wrong')
