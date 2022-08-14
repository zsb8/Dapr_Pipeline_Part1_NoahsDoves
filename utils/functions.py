import re
import html
import uuid
import time
import pandas as pd


def clean_address(address):
    """
    Delete 'Remote' and "Outside Canada/International" etc
    :param address: (str)
    :return cleaned_address: (str)
    """
    cleaned_address = ""
    if len(address) > 0:
        address = clean_stringjunk(address)
        if address.lower() in ('po', 'remote'):
            address = ''
        address = address.lower().replace('c/o ', '').strip()
        address = address.replace('Remote', '').strip()
        address = address.replace('Outside Canada/International', '').strip()
        if address[-1] == ',':
            address = address[0:-1].strip()
        if address[0] == ',':
            address = address[1:].strip()
        cleaned_address = address
    return cleaned_address


def clean_stringjunk(words):
    """
    Clean the stringjunk from words,such as '\n\t\t\t', such as space, such as ',xxxx,'
    :param words:(str)
    :return result:(str)
    """
    temp = words.encode('raw_unicode_escape').decode('utf-8')
    temp = html.unescape(temp)
    temp = temp.replace('\\n', '').strip()
    temp = temp.replace('\\t', '').strip()
    temp = temp.replace('<br />', '').strip()
    temp = temp.replace('<br/>', '').strip()
    temp = temp.replace('</br />', '').strip()
    temp = re.sub(r'(?i)n/a', '', temp)
    temp = temp.replace('\\r\\n', '').strip()
    temp = temp.replace('-------', '').strip()
    temp = temp.replace(', ', ',').strip()
    temp = temp.replace(' ,', ',').strip()
    temp = temp.replace(',,', ',').strip()
    temp = temp.replace('.,', ',').strip()
    temp = temp.replace('–', ' ').strip()
    temp = temp.replace('  ', ' ').strip()
    temp = temp.strip(',')
    result = temp
    return result


def extract_postcode(input_text):
    """
    Get the postal code from the region_locality_postcode. If get nothing, will return empty str "".
    Use the PostalCodeDatabase() to judge whether this is a really postal code.
    :param input_text: (str)
            such as 'Toronto,Ontario,M5S 1H7' from 'christiancareerscanada'
            such as 'Burlington,ON L7R4M2' or 'ikcawillhC,BC V2P 0J1'  from 'christiancharityjobs'
    :return postal_code: (str) 'M5S 1H7' Canadian postal codes are six characters with this format: A1A 1A1
    """
    if input_text:
        pattern = r'(?P<post_code>[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ -]?\d[ABCEGHJ-NPRSTV-Z]\d)'
        postal_code = extract_by_re(pattern, 'post_code', input_text)
        if not postal_code:
            # If extract_postcode fails to extract a standard postal code, then clean data and then try again.
            input_text = clean_address(input_text)
            postal_code = extract_by_re(pattern, 'post_code', input_text)
        if len(postal_code) == 6:
            # 'M3B2R2'
            result = postal_code[0:3] + " " + postal_code[3:6]
        else:
            # 'M5S 1H7' or ''
            result = postal_code
    else:
        result = input_text
    return result.upper()


def extract_city_province(region_locality_postcode, postcode):
    """
    Get the region info (city and province) from region_locality_postcode.
    First delete postcode from region_locality_postcode, then clean the data.
    IF find 'Remote' or 'Internet' in it, return empty.('christiancareerscanada')
    :param region_locality_postcode: (str)
                such as 'Toronto,Ontario,M5S 1H7' from 'christiancareerscanada'
                such as 'Burlington,ON L7R4M2' or 'ikcawillhC,BC V2P 0J1'  from 'christiancharityjobs'
    :param postcode: (str) such as 'M5S 1H7'
    :return city_province: (str)
    """
    city_province = ''
    if region_locality_postcode:
        # such as 'St. Catherines,Ontario'
        region_lower = region_locality_postcode.lower()
        region_lower = region_lower.replace('st.', '').strip()
        if any([region_lower.find('remote') > -1,  region_lower.find('international') > -1]):
            return city_province
        else:
            cleaned_region = clean_address(region_locality_postcode)
            cleaned_region = re.sub(r'(?i)' + postcode, '', cleaned_region)
            if len(postcode) == 7:  # 'M5S 1H7'
                postcode = postcode.replace(' ', '')
                cleaned_region = re.sub(r'(?i)' + postcode, '', cleaned_region)
            city_province = clean_address(cleaned_region)
    # such as 'Oakbank,Manitoba,R5N 0A8', the postcode is wrong, so here input postcode is empty
    if len(city_province.split(',')) == 3 and postcode == '':
        city_province = city_province.split(',')[0].strip() + ',' + city_province.split(',')[1].strip()
    return city_province


def extract_by_re(pattern, parameter, input_text):
    """
    Extract the result from input_text by Regular expression
    :param pattern:(str) Such as r'<div class="c-address">(?P<location>.+?)</div>'
    :param parameter:(str) Such as 'location'
    :param input_text:(str) Such as '<div class="c-address">501 Imperial Rd N<br />Guelph, Ontario, N1H 6T9</br /></div>'
    :return result:(str)
    """
    match = re.search(pattern, input_text, re.S)
    result = match.group(parameter).strip() if match else ''
    return result


def compare(df_web, df_db):
    """
    Two dataframe, df_web is from the scrapy and df_db is from the MongdoDB.
    They all have the 'url' column, judge new data by it.
    Compare them and only find the new data of df_web.
    :param df_web:(df) Data from the scrapy. Only url column.
    :param df_db:(df) Data from the MongdoDB. Only url column.
    :return df_new:(df) Only the new data in df_web. Add new column ['_id', 'scrape_date', 'isExpired']
    :return df_expired:(df) Only the expired url in df_db.
    """
    df_expired = pd.DataFrame(columns=["url"])
    if df_db.empty:
        print("!DB is empty")
        df_new = df_web
    else:
        print("DB has data. Begin to compare.")
        df = df_web.merge(df_db, how="outer", on='url', indicator='i', suffixes=('', '_right'))
        df_new = df.loc[df["i"] == 'left_only'].drop('i', axis=1)
        df_expired = df.loc[df["i"] == 'right_only'].drop('i', axis=1)
    if not df_new.empty:
        df_new['_id'] = df_new['url'].apply(lambda x: str(uuid.uuid4()))
        df_new['scrape_date'] = time.strftime('%Y-%m-%d', time.localtime())
        df_new['isExpired'] = 'False'
        df_new.reset_index(drop=True, inplace=True)
    if not df_expired.empty:
        df_expired = df_expired.loc[:, ['url']]
        df_expired.reset_index(drop=True, inplace=True)
    return df_new, df_expired
