import zipfile
from collections import OrderedDict

import rows
import xmltodict

from utils import normalize_key


DOCUMENT_TYPES = (
    "Combustivel",
    "Contrato",
    "Convenio",
    "Despesa",
    "Diarias",
    "Licitacao",
    "Obra",
    "Relacionamentos",
)
# TODO: use detect_tce_schema to get fields
METADATA = {
    "licitacao": {
        "internal_filename": "Licitacao.xml",
        "key_name": "Licitacao",
        "fields": OrderedDict(
            [
                ("cdIBGE", rows.fields.TextField),
                ("nmMunicipio", rows.fields.TextField),
                ("idPessoa", rows.fields.IntegerField),
                ("nmEntidade", rows.fields.TextField),
                ("idLicitacao", rows.fields.IntegerField),
                ("dsModalidadeLicitacao", rows.fields.TextField),
                ("nrLicitacao", rows.fields.IntegerField),
                ("nrAnoLicitacao", rows.fields.IntegerField),
                ("nrEditalOrigem", rows.fields.IntegerField),
                ("nranoEditalOrigem", rows.fields.IntegerField),
                ("dtEdital", rows.fields.DateField),
                ("dtAbertura", rows.fields.DateField),
                ("vlLicitacao", rows.fields.DecimalField),
                ("dtEnvio", rows.fields.DateField),
                ("dsNaturezaLicitacao", rows.fields.TextField),
                ("dsAvaliacaoLicitacao", rows.fields.TextField),
                ("dsClassificacaoObjetoLicitacao", rows.fields.TextField),
                ("dsRegimeExecucaoLicitacao", rows.fields.TextField),
                ("dsTipoSituacaoLicitacao", rows.fields.TextField),
                ("dtOcorrencia", rows.fields.DateField),
                ("dsObjeto", rows.fields.TextField),
                ("dsClausulaProrrogacao", rows.fields.TextField),
                ("ultimoEnvioSIMAMNesteExercicio", rows.fields.TextField),
                ("DataReferencia", rows.fields.TextField),
            ]
        ),
    },
    "licitacao_participante": {
        "internal_filename": "LicitacaoParticipante.xml",
        "key_name": "LicitacaoParticipante",
        "fields": OrderedDict(
            [
                ("cdIBGE", rows.fields.TextField),
                ("nmMunicipio", rows.fields.TextField),
                ("idPessoa", rows.fields.IntegerField),
                ("nmEntidade", rows.fields.TextField),
                ("idLicitacao", rows.fields.IntegerField),
                ("sgDocParticipanteLicitacao", rows.fields.TextField),
                ("nrDocParticipanteLicitacao", rows.fields.TextField),
                ("nmParticipanteLicitacao", rows.fields.TextField),
                ("ultimoEnvioSIMAMNesteExercicio", rows.fields.TextField),
                ("DataReferencia", rows.fields.TextField),
            ]
        ),
    },
    "licitacao_vencedor": {
        "internal_filename": "LicitacaoVencedor.xml",
        "key_name": "LicitacaoVencedor",
        "fields": OrderedDict(
            [
                ("cdIBGE", rows.fields.TextField),
                ("nmMunicipio", rows.fields.TextField),
                ("idPessoa", rows.fields.TextField),
                ("nmEntidade", rows.fields.TextField),
                ("idlicitacao", rows.fields.TextField),
                ("nrAnoLicitacao", rows.fields.TextField),
                ("nrLicitacao", rows.fields.TextField),
                ("dsModalidadeLicitacao", rows.fields.TextField),
                ("nmPessoa", rows.fields.TextField),
                ("nrDocumento", rows.fields.TextField),
                ("nrLote", rows.fields.TextField),
                ("nrItem", rows.fields.TextField),
                ("nrQuantidade", rows.fields.TextField),
                ("idUnidadeMedida", rows.fields.TextField),
                ("dsUnidadeMedida", rows.fields.TextField),
                ("vlMinimoUnitarioItem", rows.fields.TextField),
                ("vlMinimoTotal", rows.fields.TextField),
                ("vlMaximoUnitarioitem", rows.fields.TextField),
                ("vlMaximoTotal", rows.fields.TextField),
                ("dsItem", rows.fields.TextField),
                ("dsFormaPagamento", rows.fields.TextField),
                ("nrPrazoLimiteEntrega", rows.fields.TextField),
                ("idTipoEntregaProduto", rows.fields.TextField),
                ("dsTipoEntregaProduto", rows.fields.TextField),
                ("nrQuantidadePropostaLicitacao", rows.fields.TextField),
                ("vlPropostaItem", rows.fields.TextField),
                ("dtValidadeProposta", rows.fields.TextField),
                ("dtPrazoEntregaPropostaLicitacao", rows.fields.TextField),
                ("nrQuantidadeVencedorLicitacao", rows.fields.TextField),
                ("vlLicitacaoVencedorLicitacao", rows.fields.TextField),
                ("nrClassificacao", rows.fields.TextField),
                ("dtHomologacao", rows.fields.TextField),
                ("ultimoEnvioSIMAMNesteExercicio", rows.fields.TextField),
                ("DataReferencia", rows.fields.TextField),
            ]
        ),
    },
}


def convert_row(data, fields):
    new = {}
    for field_name, field_type in fields.items():
        value = data.pop("@" + field_name, "").strip()
        if field_type is rows.fields.DateField:
            value = value.replace("T", " ").split()[0]
        new[field_name] = value
    assert not data
    return {normalize_key(key): value for key, value in new.items()}


def parse_xml_from_zip(zip_filename, internal_name, key_name=None):

    # Get file object
    zf = zipfile.ZipFile(zip_filename)
    fobj = None
    for file_info in zf.filelist:
        if file_info.filename.endswith(internal_name):
            fobj = zf.open(file_info.filename)
            break
    if fobj is None:
        raise ValueError(f'"{internal_name}" not found inside "{filename}"')

    # Get data from XML
    xml = fobj.read()
    parsed = xmltodict.parse(xml)
    if key_name is None:
        keys = list(parsed["root"].keys())
        assert len(keys) == 1
        key_name = keys[0]

    return parsed["root"][key_name]


def parse(filename, file_type):
    metadata = METADATA[file_type]
    fields = metadata["fields"]
    internal_filename = metadata["internal_filename"]
    key_name = metadata["key_name"]
    data = [
        convert_row(row, fields)
        for row in parse_xml_from_zip(filename, internal_filename, key_name)
    ]
    return rows.import_from_dicts(data, force_types=fields)


def parse_licitacao(year, city_code):
    # TODO: adicionar codibge, nome municipio e ano nos 3 arquivos
    filename = DOWNLOAD_PATH / f"{year}_{city_code}_Licitacao.zip"

    result1 = parse(filename, "licitacao")
    rows.export_to_csv(result1, OUTPUT_PATH / f"licitacao-{city_code}-{year}.csv")

    result2 = parse(filename, "licitacao_participante")
    rows.export_to_csv(
        result2, OUTPUT_PATH / f"licitacao-participante-{city_code}-{year}.csv"
    )

    result3 = parse(filename, "licitacao_vencedor")
    rows.export_to_csv(
        result3, OUTPUT_PATH / f"licitacao-vencedor-{city_code}-{year}.csv"
    )


if __name__ == "__main__":
    from settings import DOWNLOAD_PATH, OUTPUT_PATH

    parse_licitacao(2018, 410690)  # 2018, Curitiba
    # TODO: rodar para todos os arquivos *_Licitacao.zip
    # TODO: fazer o mesmo para *_Obra.zip e outros tipos de arquivo
