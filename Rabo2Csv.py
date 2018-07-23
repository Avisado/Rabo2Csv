import pandas as pd
import argparse


def toFloat(cell_value):
    cell_value = cell_value.replace('+', '').replace('.', '').replace(',', '.')
    if cell_value:
        cell_value = float(cell_value)
    else:
        cell_value = 0.00
    return cell_value


def csv_to_df(file):

    # Inlezen csv bestand van Rabobank
    df = pd.read_csv(
        file,
        sep=',',
        converters={  # Converteer bedragkolommen naar amerikaanse notatie, 2 decimalen
            'Bedrag': toFloat,
            'Saldo na trn': toFloat,
            'Oorspr bedrag': toFloat,
            'Koers': toFloat,
        },
        dtype={  # Converteer bepaalde kolommen expliciet naar tekst
            'Volgnr': str,
            'Naam initi\xebrende partij': str,
            'Batch ID': str,
            'Betalingskenmerk': str,
            'Omschrijving-3': str,
            'Reden retour': str,
            'Oorspr munt': str,
        }
    )
    print('Bestand %s, aantal records: %s\nBestand opgeslagen in dataframe' % (file, len(df)))

    return df


def post_process_df(df):

    # Opschonen dataframe, verwijderen ongewenste karakters
    df = df.replace('\\|\x09|\x0d|\x0a|;|,', '', regex=True)
    df = df.replace('\x20+', '\x20', regex=True)
    df = df.fillna('')
    print('Dataframe opgeschoond')

    # Aanmaken nieuewe velden t.b.v. import in Xero
    df['Date'] = df['Rentedatum'].str[-2:] + '-' + df['Rentedatum'].str[5:7] + '-' + df['Rentedatum'].str[:4]
    df['Amount'] = df['Bedrag']
    df['Payee'] = df['Naam tegenpartij']
    df['Description'] = df['Omschrijving-1']
    df['Reference'] = ''
    df['Check Number'] = ''
    print('Extra kolommen aangemaakt')

    return df


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='Geef csv-bestandsnaam van Rabobank')
    args = parser.parse_args()
    file_in = args.filename
    file_out = 'from_%s_to_xero.csv' % file_in[:-4]
    print('Bestand van Rabobank: %s' % file_in)

    df_rabo = csv_to_df(file_in)
    df_rabo = post_process_df(df_rabo)

    # Pak enkel de kolommen die nodig zijn voor import in Xero en maak csv-bestand aan
    df_xero = df_rabo.loc[:, ['Date', 'Amount', 'Payee', 'Description', 'Reference', 'Check Number']]
    df_xero.to_csv(file_out, sep=',', index=False)
    print('Bestand voor Xero: %s' % file_out)

    print("Programma klaar")

