const express = require('express');
const app = express();
const port = 8080;
const axios = require('axios')

app.get('/api/consultar/', async (req, res) => {
const { cpf, nb } = req.query

  if (!cpf || !nb ) {
    return res.status(400).json({ error: 'Parâmetros CPF e NB obrigatorios.' })
  }

  const info = await axios.get(`https://queromaiscredito.app/DataPrev/e-consignado/beneficios/cartao_consulta_in100.php?https://armazem.capitalbank.systems/_dataPrev/${cpf}/Resumo-${cpf}-${nb}.json `)  `)
  
return res.status(200).json(info.data)
  
})

app.listen(port, () => {
    console.log(`Servidor rodando em http://localhost:${port}`);
});
