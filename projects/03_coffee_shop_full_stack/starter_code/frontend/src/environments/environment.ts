/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'full-s-d', // the auth0 domain prefix
    audience: 'Coffee App', // the audience set for the auth0 app
    clientId: 'A2wKjm5vtQw4UB2nMqWV92U5bYH5sB6k', // the client id generated for the auth0 app
    callbackURL: 'https://localhost:5000', // the base url of the running ionic application.
  }
};

