<template>
  <div class="hello">
    <!-- <h1>{{ msg }}</h1>
    <p>
      For a guide and recipes on how to configure / customize this project,<br>
      check out the
      <a href="https://cli.vuejs.org" target="_blank" rel="noopener">vue-cli documentation</a>.
    </p>
    <h3>Installed CLI Plugins</h3>
    <ul>
      <li><a href="https://github.com/vuejs/vue-cli/tree/dev/packages/%40vue/cli-plugin-babel" target="_blank" rel="noopener">babel</a></li>
      <li><a href="https://github.com/vuejs/vue-cli/tree/dev/packages/%40vue/cli-plugin-eslint" target="_blank" rel="noopener">eslint</a></li>
    </ul>
    <h3>Essential Links</h3>
    <ul>
      <li><a href="https://vuejs.org" target="_blank" rel="noopener">Core Docs</a></li>
      <li><a href="https://forum.vuejs.org" target="_blank" rel="noopener">Forum</a></li>
      <li><a href="https://chat.vuejs.org" target="_blank" rel="noopener">Community Chat</a></li>
      <li><a href="https://twitter.com/vuejs" target="_blank" rel="noopener">Twitter</a></li>
      <li><a href="https://news.vuejs.org" target="_blank" rel="noopener">News</a></li>
    </ul>
    <h3>Ecosystem</h3>
    <ul>
      <li><a href="https://router.vuejs.org" target="_blank" rel="noopener">vue-router</a></li>
      <li><a href="https://vuex.vuejs.org" target="_blank" rel="noopener">vuex</a></li>
      <li><a href="https://github.com/vuejs/vue-devtools#vue-devtools" target="_blank" rel="noopener">vue-devtools</a></li>
      <li><a href="https://vue-loader.vuejs.org" target="_blank" rel="noopener">vue-loader</a></li>
      <li><a href="https://github.com/vuejs/awesome-vue" target="_blank" rel="noopener">awesome-vue</a></li>
    </ul> -->
    <div style="margin-top: 3rem;">
      <vue-tree-list
        @click="onClick"
        @change-name="onClick"
        @delete-node="onDel"
        @add-node="onAddNode"
        @drop="onDrop"
        @drop-before="onDropBefore"
        :model="structure"
        default-tree-node-name="new node"
        default-leaf-node-name="new leaf"
        v-bind:default-expanded="true"
      >
        <template v-slot:leafNameDisplay="slotProps">
          <span>
            {{ slotProps.model.name }} <span class="muted">#{{ slotProps.model.id }}</span>
          </span>
        </template>
        <span class="icon" slot="addTreeNodeIcon">📂</span>
        <span class="icon" slot="addLeafNodeIcon">＋</span>
        <span class="icon" slot="editNodeIcon">📃</span>
        <span class="icon" slot="delNodeIcon">✂️</span>
        <span class="icon" slot="leafNodeIcon">🍃</span>
        <span class="icon" slot="treeNodeIcon">🌲</span>
      </vue-tree-list>
    </div>
    {{structure}}
  </div>
</template>

<script>
// import { VueTreeList, TreeNode } from 'vue-tree-list';
import { VueTreeList, Tree } from 'vue-tree-list';
import axios from 'axios';
export default {
  name: 'HelloWorld',
  components: {
    VueTreeList
  },
  props: {
    msg: String
  },
  data() {
    return {
      structure: new Tree([])
    }
  },
  mounted() {
    this.structureLoad()
  },
  methods: {
    structureLoad(){
      return axios.get('/API/v1.0.0/organization/structure/elements?dbg=true')
        .then((response) => {
          function _dfs(oldNode) {
            var newNode = {}
            for (var k in oldNode) {
              if (k !== 'children' && k !== 'parent') {
                var value
                if (k === "deletable") {
                  value = Boolean(oldNode[k])
                  newNode["delNodeDisabled"] = !value
                } else if (k === "movable") {
                  value = Boolean(oldNode[k])
                  newNode["dragDisabled"] = !value
                } else if (k === "type") {
                  if (oldNode[k] === 1) {
                    newNode["isLeaf"] = false
                  } else if (oldNode[k] === 2) {
                    newNode["isLeaf"] = true
                  }
                } else {
                  newNode[k] = oldNode[k]
                }
              }
            }

            if (oldNode.children && oldNode.children.length > 0) {
              newNode.children = []
              for (var i = 0, len = oldNode.children.length; i < len; i++) {
                newNode.children.push(_dfs(oldNode.children[i]))
              }
            }
            return newNode
          }

          this.structure = new Tree(
            [
              _dfs(response.data[0])
            ]
          );
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },

    onDrop(node){
      // console.log(node.node.id + ' into '  + node.target.id);
      return axios.put(`/API/v1.0.0/organization/structure/elements/${node.node.id}?dbg=true&parent=${node.target.id}`)
        .then((response) => {
          console.log(response.data);
          node.node.moveInto(node.target);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error.response.data);
        });
    },

    onDropBefore(node){
      // console.log(node.node.id + ' before '  + node.target.id);
      return axios.put(`/API/v1.0.0/organization/structure/elements/${node.node.id}?dbg=true&before=${node.target.id}`)
        .then((response) => {
          console.log(response.data);
          node.node.moveBefore(node.target);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error.response.data);
        });
    },

    onDel(node) {
     // console.log(node.id)
     return axios.delete(`/API/v1.0.0/organization/structure/elements/${node.id}?dbg=true`)
       .then((response) => {
         console.log(response.data);
         node.remove()
       })
       .catch((error) => {
         // eslint-disable-next-line
         console.error(error.response.data);
       });
    },

   onChangeName(params) {
     console.log(params)
   },

   onAddNode(params) {
     // console.log(params)
     return axios.post(`/API/v1.0.0/organization/structure/elements?dbg=true&type=${params.isLeaf ? 2 : 1}&parent=${params.pid}`)
       .then((response) => {
         params.id = response.data.node.id;
         if (response.data.node.type === 2) {
           params.isLeaf = true;
         } else {
           params.isLeaf = false;
         }
         params.name = response.data.node.name
         console.log(response.data);
       })
       .catch((error) => {
         // eslint-disable-next-line
         console.error(error.response.data);
       });
   },

   onClick(params) {
     console.log(params)
   },

   getNewTree() {
     var vm = this
     function _dfs(oldNode) {
       var newNode = {}

       for (var k in oldNode) {
         if (k !== 'children' && k !== 'parent') {
           if (k === "deletable") {
             newNode["delNodeDisabled"] = !!+oldNode[k]
           } else {
             newNode[k] = oldNode[k]
           }
         }
       }

       if (oldNode.children && oldNode.children.length > 0) {
         newNode.children = []
         for (var i = 0, len = oldNode.children.length; i < len; i++) {
           newNode.children.push(_dfs(oldNode.children[i]))
         }
       }
       return newNode
     }

     vm.newTree = _dfs(vm.structure)
   }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  h3 {
    margin: 40px 0 0;
  }
  ul {
    list-style-type: none;
    padding: 0;
  }
  li {
    display: inline-block;
    margin: 0 10px;
  }
  a {
    color: #42b983;
  }
</style>

<style lang="scss" rel="stylesheet/sass">
  .vtl {
    .vtl-drag-disabled {
      background-color: #d0cfcf;
      &:hover {
        background-color: #d0cfcf;
      }
    }
    .vtl-disabled {
      background-color: #d0cfcf;
    }
  }
</style>

<style lang="scss" rel="stylesheet/sass" scoped>
  .icon {
    &:hover {
      cursor: pointer;
    }
  }

  .muted {
    color: gray;
    font-size: 80%;
  }
</style>
