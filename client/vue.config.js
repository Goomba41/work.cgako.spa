module.exports = {
  devServer: {
    host: '0.0.0.0',
    hot: true,
    disableHostCheck: true,
    proxy: {
      "/API/v1.0.0":{
        target: "http://devserver.gaspiko.lc:5000/API/v1.0.0",
        changeOrigin: true,
        pathRewrite:{
          '^/API/v1.0.0':""
        },
        logLevel: 'debug'
      }
    }
  }
}
