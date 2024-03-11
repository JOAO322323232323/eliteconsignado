const express = require('express');
const app = express();
const port = 9080;
const axios = require('axios')
const wio = require('wio.db')
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { uid } = require('uid')
const csv = require('csv-parser');
const excel4node = require('excel4node');
const moment = require('moment');

const logins = new wio.JsonDatabase({
  databasePath: "database/logins.json",
});

const querys = new wio.JsonDatabase({
  databasePath: "database/querys.json",
});

app.use(bodyParser.json());

let pendente = false

function resetarLogins() {

  const agora = moment();

  if (agora.hour() === 0 && agora.minute() === 0) {
  
    const arrayToAdd = logins.get('suspensos')

    arrayToAdd.forEach(async login => {
      const indexToDelete = logins.get("suspensos").findIndex((option) => option === `${login}`);
       
      if (indexToDelete !== -1) {
        const a = logins.get("suspensos");
        const removed = a.splice(indexToDelete, 1);
        await logins.set("suspensos", a);

        logins.push('users', removed.toString())
      }
      
    });
   
  }
}

setInterval(resetarLogins, 60000);


function gerarNumeroAleatorio(min, max) {
  const range = max - min + 1;
  const randomNumber = Math.floor(Math.random() * range) + min;
  return randomNumber;
}


function gerarSeteNumerosAleatoriosString() {
  const numerosAleatorios = [];
  const quantidadeNumeros = 7;
  const minimo = 0; 
  const maximo = 9; 

  for (let i = 0; i < quantidadeNumeros; i++) {
    const numeroAleatorio = gerarNumeroAleatorio(minimo, maximo);
    numerosAleatorios.push(numeroAleatorio);
  }


  const numerosString = numerosAleatorios.join('');

  return numerosString;
}


async function makeRequest(login, cpf, nb, id, cpf_rep) {

  
  const requestData = {
    system: 'FUNCAO',
    cod_operator: login,
    name: 'fdsgfgffbdgh',
    cpf: cpf,
    cpf_represent: cpf_rep || '',
    tel: `(21)99${gerarSeteNumerosAleatoriosString()}`,
    cod_beneficio: nb,
    enviar_sms: 'false',
    enviar_whatsapp: 'true',
    enviar_email: 'false',
  };
  
  const apiUrl = 'https://queromaiscredito.app/DataPrev/e-consignado/beneficios/cartao_consulta_in100.php';
  
  axios.post(apiUrl, requestData, {
    headers: {
      'Content-Type': 'application/json; charset=UTF-8',
    },
  })
    .then(async response => {
      if (response.data.includes("O termo de autorização de consulta foi enviado pata o Cliente")) {
        querys.add(`${id}.success`, 1)

        const req = await axios.get(`http://62.72.8.214:9080/api/consultar?cpf=${cpf}&nb=${nb}`)

       querys.push(`${id}.data`, req.data)

      } else if (response.data.includes('Erro 1')) {
        querys.push(`${id}.retestar`, { cpf: cpf, nb: nb, rep: cpf_rep || "" })
        logins.push('suspensos', login)
        const indexToDelete = logins.get("users").findIndex((option) => option === `${login}`);
       
      if (indexToDelete !== -1) {
        const a = logins.get("users");
        const removed = a.splice(indexToDelete, 1);
        await logins.set("users", a);
      }
        
      } else {
        querys.add(`${id}.fail`, 1)
        fs.appendFileSync('errors.txt', response.data+'\n')
      }
    })
    .catch(error => {
      console.error(error);
    });
  
}

async function getRandomLogin() {
  const allLogins = await logins.get('users')
  const randomIndex = Math.floor(Math.random() * allLogins.length);
 return allLogins[randomIndex]
}

async function sendQueryToApi(id) {

  const filePath = await querys.get(`${id}.filePath`); 

const dataArray = [];

fs.createReadStream(filePath, { encoding: 'utf-8' })
  .pipe(csv({ separator: ';' }))
  .on('data', (row) => {
    dataArray.push(row);
  })
  .on('end', async () => {

    pendente = true

    for (let i = 0; i < dataArray.length; i++) {
      const login = await getRandomLogin();
  
      try {
        await makeRequest(login, dataArray[i].CPF, dataArray[i].NB, id, dataArray[i].CPF_REP);
        console.log(`Request for data point ${i + 1} completed successfully.`);
      } catch (error) {
        console.error(`Error processing data point ${i + 1}:`, error);
       
      }
  
    
      if (i < dataArray.length - 1) {
        await new Promise((resolve) => setTimeout(resolve, 20000)); 
      }
    }
  
  
    fs.unlinkSync(`${filePath}`)
    console.log('Completo')
    pendente = false
    await querys.set(`${id}.status`, 'finalizado')

  })
  .on('error', (error) => {
    console.error('Erro ao ler o arquivo CSV:', error.message);
  });



}

app.get('/api/consultar-campanha', async  (req, res) => {
  const { id } = req.query;

  if (!id) {
    return res.status(400).json({ error: 'Missing id in the query' });
  }

  if (querys.get(`${id}.status`) === 'pendente') {
    return res.status(400).json({ error: 'Essa campanha ainda está pendente' });
  }

  const allCpf = querys.get(`${id}.data`)

  if (!allCpf) {
    return res.status(400).json({ error: 'Não retornou nenhum resultado' });
  }


  const dados = await querys.get(`${id}.data`)

  const workbook = new excel4node.Workbook();


const worksheet = workbook.addWorksheet('Dados');


const headers = Object.keys(dados[0]);


for (let i = 0; i < headers.length; i++) {
  worksheet.cell(1, i + 1).string(headers[i]);
}


for (let i = 0; i < dados.length; i++) {
  const row = i + 2;
  for (let j = 0; j < headers.length; j++) {
    const key = headers[j];
   
    let value = dados[i][key];
    if (typeof value === 'object' && value !== null) {
      value = value.descricao || value.codigo;
    }
    worksheet.cell(row, j + 1).string(value.toString());
  }
}


await workbook.write('dados.xlsx')

setTimeout(() => {
  const buffer = fs.readFileSync('dados.xlsx');
  const base64 = Buffer.from(buffer).toString('base64');
  fs.unlinkSync('dados.xlsx')
  res.status(200).json({ success: querys.get(`${id}.success`), fail: querys.get(`${id}.fail`), excelBase64: base64 })
}, 5000)



})

app.post('/api/criar-campanha', (req, res) => {
  const { base64Data } = req.body;

  if (pendente) {
    return res.status(400).json({ error: 'Outra consulta está em processamento, tente novamente mais tarde.'})
  }

  if (!base64Data) {
    return res.status(400).json({ error: 'Missing base64Data in the request body' });
  }

  const id = uid(20)

  const binaryData = Buffer.from(base64Data, 'base64');

  const rndNum = Math.floor(Math.random() * 999999);


  const filePath = path.join(__dirname, `${rndNum}.csv`);


  fs.writeFile(filePath, binaryData, async (err) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'Failed to save the file' });
    }

    await querys.set(`${id}.filePath`, `${rndNum}.csv`)
    await querys.set(`${id}.success`, 0)
    await querys.set(`${id}.fail`, 0)
    await querys.set(`${id}.status`, 'pendente')
     sendQueryToApi(id)
    res.status(200).json({ message: 'File saved successfully', id: id });
  });
});


app.get('/api/consultar/', async (req, res) => {
const { cpf, nb, rep } = req.query

  if (!cpf || !nb ) {
    return res.status(400).json({ error: 'Parâmetros CPF e NB obrigatorios.' })
  }

  const login = await getRandomLogin();

  const requestData = {
    system: 'FUNCAO',
    cod_operator: login,
    name: 'fdsgfgffbdgh',
    cpf: cpf,
    cpf_represent: rep || '',
    tel: `(21)99${gerarSeteNumerosAleatoriosString()}`,
    cod_beneficio: nb,
    enviar_sms: 'false',
    enviar_whatsapp: 'true',
    enviar_email: 'false',
  };
  
  const apiUrl = 'https://queromaiscredito.app/DataPrev/e-consignado/beneficios/cartao_consulta_in100.php';
  
  axios.post(apiUrl, requestData, {
    headers: {
      'Content-Type': 'application/json; charset=UTF-8',
    },
  })
    .then(async response => {
    
      if (response.data.includes("O termo de autorização de consulta foi enviado pata o Cliente")) {
       
        const info = await axios.get(`https://queromaiscredito.app/DataPrev/e-consignado/beneficios/cartao_consulta_in100.php?https://armazem.capitalbank.systems/_dataPrev/${cpf}/Resumo-${cpf}-${nb}.json `)
  
        return res.status(200).json(info.data)


      } else {
       return res.status(400).json({ error: 'Não foi possivel concluir a consulta'})
      }
    })
    .catch(error => {
      console.error(error);
    });


  
})

app.listen(port, () => {
    console.log(`Servidor rodando em http://localhost:${port}`);
});
